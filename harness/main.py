import asyncio
import json
import os

from dotenv import load_dotenv
from anthropic import Anthropic
from mcp.client import Client
import redis

load_dotenv()


def get_api_key():
    # Docker Compose mounts a file-based secret at a fixed path,
    # /run/secrets/<name> - if it's there, we're containerised; if
    # not, fall back to ANTHROPIC_API_KEY from the environment (via
    # .env), for running this locally.
    secret_path = "/run/secrets/anthropic_api_key"
    if os.path.exists(secret_path):
        with open(secret_path) as f:
            return f.read().strip()
    return os.getenv("ANTHROPIC_API_KEY")


client = Anthropic(api_key=get_api_key())
redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, decode_responses=True)

MODEL_ID = "claude-sonnet-5"
MAX_TOKENS = 1024
MAX_ITERATIONS = 5
REDIS_KEY = "opspilot:conversation"
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")

SYSTEM_PROMPT = (
    "You are OpsPilot, an autonomous agent investigating issues in the order queue. "
    "You have access to three tools: get_queue_status, get_recent_errors, and search_knowledge_base. "
    "Use these tools as needed to investigate the issue thoroughly, and continue until you can provide a complete and confident diagnosis."
)


def get_text(content):
    # Find the first text block in a response's content list.
    for block in content:
        if block.type == "text":
            return block.text
    return "(no text in response)"


def get_saved_text(content):
    # Same idea as get_text, but for a *loaded* message's content -
    # a list of plain dicts (from json.loads), not SDK objects.
    for block in content:
        if block["type"] == "text":
            return block["text"]
    return "(no text in response)"


def save_conversation(messages):
    redis_client.set(REDIS_KEY, json.dumps(messages))
    print(f"Conversation saved to Redis with {len(messages)} messages.")


async def main():
    # Load a previous conversation from Redis, if one was saved -
    # otherwise start a fresh one with the initial investigation prompt.
    existing_conversation = redis_client.get(REDIS_KEY)

    if existing_conversation is not None:
        messages = json.loads(existing_conversation)
        print(f"Loaded existing conversation from Redis with {len(messages)} messages.")
    else:
        messages = [{"role": "user", "content": "Check the order queue and let me know if there are any related errors."}]

    # A response is still owed whenever the last message is from the
    # user - whether that's a brand-new conversation or one that got
    # interrupted mid-investigation. Otherwise, there's nothing to do.
    if messages[-1]["role"] == "user":
        # Connect to the MCP server and ask it what tools it offers,
        # converting its listing into the shape Claude's API expects.
        async with Client(MCP_SERVER_URL) as mcp_client:
            tools_result = await mcp_client.list_tools()
            tool_schemas = [
                {"name": t.name, "description": t.description, "input_schema": t.input_schema}
                for t in tools_result.tools
            ]

            # Keep talking to Claude until it gives a final answer, or
            # we hit the safety cap on how many rounds this can take.
            for _ in range(MAX_ITERATIONS):
                # Ask Claude what to do next, given the conversation so far.
                response = client.messages.create(
                    model=MODEL_ID,
                    max_tokens=MAX_TOKENS,
                    system=SYSTEM_PROMPT,
                    tools=tool_schemas,
                    messages=messages,
                )
                messages.append({"role": "assistant", "content": [block.model_dump() for block in response.content]})

                # Claude is done (or got cut off) - show the answer and stop.
                if response.stop_reason == "end_turn":
                    print("Final answer:", get_text(response.content))
                    save_conversation(messages)
                    break
                elif response.stop_reason != "tool_use":
                    print(f"Answer may be incomplete (stop_reason: {response.stop_reason}):")
                    print(get_text(response.content))
                    save_conversation(messages)
                    break

                # Otherwise, Claude wants tool(s) run. Claude can request
                # more than one tool call in a single turn - collect and
                # execute every tool_use block, not just the first.
                tool_results = []
                for block in response.content:
                    if block.type != "tool_use":
                        continue

                    # Run the tool via the MCP server, rather than
                    # calling a local Python function directly. Unknown
                    # tool names and tool-side failures are the
                    # server's problem now, reported back via
                    # result.is_error - the except below only covers
                    # the call to the server itself failing.
                    try:
                        result = await mcp_client.call_tool(block.name, block.input)
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": get_text(result.content),
                                "is_error": result.is_error,
                            }
                        )
                    except Exception as e:
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": f"Error calling MCP server for tool '{block.name}': {e}",
                                "is_error": True,
                            }
                        )

                # Send the tool results back, and checkpoint progress
                # before the next round in case something interrupts us.
                messages.append({"role": "user", "content": tool_results})
                save_conversation(messages)
            else:
                # Runs only if the loop used up every iteration without a
                # `break` - i.e. Claude never stopped asking for tools.
                print(f"Stopped after {MAX_ITERATIONS} iterations without a final answer.")
    else:
        # Nothing new to do - just show the cached answer.
        print("Conversation already finished. Last answer:")
        print(get_saved_text(messages[-1]["content"]))


# Entry point - runs the async flow above to completion.
asyncio.run(main())
