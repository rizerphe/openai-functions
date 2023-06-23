"""Type definitions for JSON data."""
from __future__ import annotations

JsonType = int | float | str | bool | list["JsonType"] | dict[str, "JsonType"] | None
