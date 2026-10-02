from dotenv import load_dotenv

load_dotenv()

from anthropic import Anthropic


def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)


def chat(messages):
    system = "You are a math tutor. you do not instantly give the answer but gently guide the student to the answer.If you find they cant  answer after many turns only then do you answer "
    message = client.messages.create(
        model=model, max_tokens=1000, messages=messages, system=system
    )
    return message.content[0].text


client = Anthropic()
model = "claude-haiku-4-5-20251001"
messages = []

print("Chat with Claude. Type 'exit' or 'quit' to stop.")

while True:
    try:
        user_input = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        break

    if not user_input:
        continue
    if user_input.lower() in ("exit", "quit"):
        break

    add_user_message(messages, user_input)
    answer = chat(messages)
    add_assistant_message(messages, answer)

    print("---")
    print(answer)
    print("---")
