import json

from dotenv import load_dotenv
from anthropic import Anthropic
import redis

load_dotenv()
client = Anthropic()
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

MODEL_ID = "claude-sonnet-5"
MAX_TOKENS = 1024
MAX_ITERATIONS = 5
REDIS_KEY = "opspilot:conversation"


def get_queue_status():
    # Dummy data standing in for a real queue status check.
    return {
        "queue_name": "OrderQueue",
        "depth": 42,
        "status": "Processing",
    }


def get_recent_errors():
    # Dummy data standing in for a real recent errors check.
    return [
        {"service": "PaymentService", "message": "Failed to process payment", "count": 5},
        {"service": "InventoryService", "message": "Stock levels low", "count": 3},
    ]


TOOL_SCHEMAS = [
    {
        "name": "get_queue_status",
        "description": "Returns the current status of the order queue.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "get_recent_errors",
        "description": "Returns a list of recent errors from various services.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
]

TOOLS = {
    "get_queue_status": get_queue_status,
    "get_recent_errors": get_recent_errors,
}


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


def save_conversation():
    redis_client.set(REDIS_KEY, json.dumps(messages))
    print(f"Conversation saved to Redis with {len(messages)} messages.")


existing_conversation = redis_client.get(REDIS_KEY)

if existing_conversation is not None:
    messages = json.loads(existing_conversation)
    print(f"Loaded existing conversation from Redis with {len(messages)} messages.")
else:
    messages = [{"role": "user", "content": "Check the order queue and let me know if there are any related errors."}]

if messages[-1]["role"] == "user":
    for _ in range(MAX_ITERATIONS):
        response = client.messages.create(
            model=MODEL_ID,
            max_tokens=MAX_TOKENS,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": [block.model_dump() for block in response.content]})

        if response.stop_reason == "end_turn":
            print("Final answer:", get_text(response.content))
            save_conversation()
            break
        elif response.stop_reason != "tool_use":
            print(f"Answer may be incomplete (stop_reason: {response.stop_reason}):")
            print(get_text(response.content))
            save_conversation()
            break

        # Claude can request more than one tool call in a single turn -
        # collect and execute every tool_use block, not just the first.
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            if block.name not in TOOLS:
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"Error: Tool '{block.name}' not found.",
                        "is_error": True,
                    }
                )
                continue

            try:
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(TOOLS[block.name]()),
                    }
                )
            except Exception as e:
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"Error executing tool '{block.name}': {str(e)}",
                        "is_error": True,
                    }
                )

        messages.append({"role": "user", "content": tool_results})
        save_conversation()
    else:
        # Runs only if the loop used up every iteration without a
        # `break` - i.e. Claude never stopped asking for tools.
        print(f"Stopped after {MAX_ITERATIONS} iterations without a final answer.")
else:
    print("Conversation already finished. Last answer:")
    print(get_saved_text(messages[-1]["content"]))
