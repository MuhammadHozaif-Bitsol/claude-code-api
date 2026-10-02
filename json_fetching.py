import json

from dotenv import load_dotenv

load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-haiku-4-5-20251001"
messages = []


def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)


def chat(messages, stop_sequences=None):
    message = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=messages,
        stop_sequences=stop_sequences or [],
    )
    return message.content[0].text


add_user_message(
    messages,
    "Return json  array with a score of top 5 tourist attractions in 2026 just an array.Json must be inside the array",
)

add_assistant_message(messages, "```json")
text = chat(messages, stop_sequences=["```"])

data = json.loads(text)
print(data)
