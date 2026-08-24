"""
OpsPilot - Stage 3: the agentic loop.

Wraps the tool-use round-trip from the previous stage in a loop that
keeps going until Claude stops asking for tools, or a safety cap on
iterations is hit. Still one tool, and no error handling around tool
execution yet - just the loop mechanics: request, check, execute
(possibly several tools at once), respond, repeat.
"""

import json

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

MODEL_ID = "claude-sonnet-5"
MAX_ITERATIONS = 5


def get_queue_status():
    """Dummy data standing in for a real queue status check."""
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

for iteration in range(MAX_ITERATIONS):
    response = client.messages.create(
        model=MODEL_ID,
        max_tokens=300,
        tools=[tool_schema],
        messages=messages,
    )
    messages.append({"role": "assistant", "content": response.content})

    if response.stop_reason != "tool_use":
        print("Final answer:", response.content[0].text)
        break

    # Claude can request more than one tool call in a single turn -
    # collect and execute every tool_use block, not just the first.
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(get_queue_status()),
                }
            )
    messages.append({"role": "user", "content": tool_results})
else:
    # Runs only if the loop used up every iteration without a
    # `break` - i.e. Claude never stopped asking for tools.
    print(f"Stopped after {MAX_ITERATIONS} iterations without a final answer.")
