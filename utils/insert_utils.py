from typing import Any

def is_multiple_insert(values: Any) -> bool:
    """
    Check if the given value is a list or tuple.
    """
    return isinstance(values, (list, tuple))