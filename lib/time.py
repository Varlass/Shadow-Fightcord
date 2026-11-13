from datetime import datetime, timezone
from beartype import beartype


@beartype
def time(format: str = "datetime"):
    """
    The function accepts the following formats:
    - 'datetime': return datetime.
    - 'float': return Unix timestamp as float.
    - 'int': return Unix timestamp as int.
    - 'str:{strftime format}': return formatted time as str.
    """

    format_type = format.lower()

    datetime_current_time = datetime.now(timezone.utc)
    if format_type == "datetime":
        return datetime_current_time

    float_current_time = datetime_current_time.timestamp()
    if format_type == "float":
        return float_current_time

    if format_type == "int":
        return int(float_current_time)

    if format_type.startswith("str:"):
        return datetime_current_time.strftime(format[4:])

    raise ValueError(f"Invalid time format: {format!r}")