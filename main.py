from dotenv import load_dotenv 
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

MODEL_ID = "claude-sonnet-5"

response = client.messages.create(
    model=MODEL_ID,
    max_tokens=200,
    messages=[{"role": "user", "content": "Write a poem about the sea."}],
)

print(response.content[0].text)
print(response.stop_reason)
print(response.usage)