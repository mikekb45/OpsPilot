import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

MODEL_ID = "claude-sonnet-5"


def get_queue_status():
    # Dummy data standing in for a real queue status check.
    return {
        "queue_name": "OrderQueue",
        "depth": 42,
        "status": "Processing",
    }


# Describes get_queue_status() to Claude. Claude only ever sees this
# schema - never the function itself.
tool_schema = {
    "name": "get_queue_status",
    "description": "Returns the current status of the order queue, including its name, depth, and processing status.",
    "input_schema": {
        "type": "object",
        "properties": {},
    },
}

messages = [{"role": "user", "content": "What is the status of the order queue?"}]

response = client.messages.create(
    model=MODEL_ID,
    max_tokens=200,
    tools=[tool_schema],
    messages=messages,
)

print(response.content)
print(response.stop_reason)

# Claude doesn't execute tools itself - it only requests one. Find the
# tool_use block among whatever came back (it may be mixed in with
# text, as seen above).
for block in response.content:
    if block.type == "tool_use":
        tool_use_block = block
        break

# Actually run the real function ourselves.
queue_status = get_queue_status()

# Send the whole conversation back, extended with Claude's tool
# request and our tool result, so Claude can finish answering.
messages.append({"role": "assistant", "content": response.content})
messages.append(
    {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_use_block.id,
                "content": json.dumps(queue_status),
            }
        ],
    }
)

final_response = client.messages.create(
    model=MODEL_ID,
    max_tokens=200,
    tools=[tool_schema],
    messages=messages,
)

print(final_response.content[0].text)
