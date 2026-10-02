"""Python functions that Claude can call as tools."""

from datetime import UTC, datetime, timedelta


def add_duration_to_datetime(
    datetime_str, duration=0, unit="days", input_format="%Y-%m-%d"
):
    # The output shows wall-clock time only, so attaching UTC does not change it.
    date = datetime.strptime(datetime_str, input_format).replace(tzinfo=UTC)

    if unit == "seconds":
        new_date = date + timedelta(seconds=duration)
    elif unit == "minutes":
        new_date = date + timedelta(minutes=duration)
    elif unit == "hours":
        new_date = date + timedelta(hours=duration)
    elif unit == "days":
        new_date = date + timedelta(days=duration)
    elif unit == "weeks":
        new_date = date + timedelta(weeks=duration)
    elif unit == "months":
        month = date.month + duration
        year = date.year + month // 12
        month = month % 12
        if month == 0:
            month = 12
            year -= 1
        day = min(
            date.day,
            [
                31,
                29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                31,
                30,
                31,
                30,
                31,
                31,
                30,
                31,
                30,
                31,
            ][month - 1],
        )
        new_date = date.replace(year=year, month=month, day=day)
    elif unit == "years":
        new_date = date.replace(year=date.year + duration)
    else:
        raise ValueError(f"Unsupported time unit: {unit}")

    return new_date.strftime("%A, %B %d, %Y %I:%M:%S %p")


def set_reminder(content, timestamp):
    print(f"----\nSetting the following reminder for {timestamp}:\n{content}\n----")


def get_current_datetime(date_format="%Y-%m-%d %H:%M:%S"):
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.now().astimezone().strftime(date_format)


# Maps the tool name Claude sends back to the Python function that runs it.
TOOL_FUNCTIONS = {
    "add_duration_to_datetime": add_duration_to_datetime,
    "set_reminder": set_reminder,
    "get_current_datetime": get_current_datetime,
}


def run_tool(tool_use_block):
    """Run the function Claude asked for and wrap the output in a tool_result block."""
    try:
        function = TOOL_FUNCTIONS[tool_use_block.name]
        output = function(**tool_use_block.input)
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_block.id,
            "content": str(output),
            "is_error": False,
        }
    # Any tool failure (bad input, unknown tool) is reported back to Claude.
    except Exception as error:  # noqa: BLE001
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_block.id,
            "content": f"Error: {error}",
            "is_error": True,
        }


def run_tools(message):
    """Run every tool_use block in Claude's message and return the tool_result blocks."""
    return [run_tool(block) for block in message.content if block.type == "tool_use"]
