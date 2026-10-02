from client import add_assistant_message, add_user_message, chat, text_from_message
from schemas import (
    add_duration_to_datetime_schema,
    get_current_datetime_schema,
    set_reminder_schema,
)
from tool_functions import run_tools

tools = [
    get_current_datetime_schema,
    add_duration_to_datetime_schema,
    set_reminder_schema,
]


def run_conversation(messages):
    """Keep calling Claude and running tools until Claude stops asking for tools."""
    while True:
        response = chat(messages, tools=tools)
        add_assistant_message(messages, response)
        print("Claude:", text_from_message(response) or "(no text)")

        if response.stop_reason != "tool_use":
            break

        tool_results = run_tools(response)
        for result in tool_results:
            print(f"  Tool result: {result['content']} (error: {result['is_error']})")
        add_user_message(messages, tool_results)

    return messages


messages = []
add_user_message(
    messages,
    "Set a reminder for my doctors appointment. Its 177 days after Jan 1st, 2027.",
)
run_conversation(messages)
