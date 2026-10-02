"""Anthropic client setup and chat helpers."""

from anthropic import Anthropic
from anthropic.types import Message
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()
model = "claude-haiku-4-5"


def _content_of(message):
    """Return the blocks of a full Message, or the value itself (string or list)."""
    return message.content if isinstance(message, Message) else message


def add_user_message(messages, message):
    """Add a user turn: a string, a list of blocks, or a full Message."""
    messages.append({"role": "user", "content": _content_of(message)})


def add_assistant_message(messages, message):
    """Add an assistant turn: a string, a list of blocks, or a full Message."""
    messages.append({"role": "assistant", "content": _content_of(message)})


def chat(messages, system=None, stop_sequences=None, tools=None):
    """Call Claude and return the whole message, not just its first text block."""
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "stop_sequences": stop_sequences or [],
    }

    if system:
        params["system"] = system
    if tools:
        params["tools"] = tools

    return client.messages.create(**params)


def text_from_message(message):
    """Join all text blocks in a message into one string."""
    return "\n".join(block.text for block in message.content if block.type == "text")
