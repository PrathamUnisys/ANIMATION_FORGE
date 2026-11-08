import os
from typing import Any


_WINDOWS_RESERVED_COMPONENTS = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


def is_safe_path_component(value: Any) -> bool:
    if (
        not isinstance(value, str)
        or not value
        or value in {".", ".."}
        or "\x00" in value
        or "/" in value
        or "\\" in value
        or ":" in value
        or value.endswith((".", " "))
        or os.path.splitdrive(value)[0]
    ):
        return False
    return value.split(".", 1)[0].upper() not in _WINDOWS_RESERVED_COMPONENTS
