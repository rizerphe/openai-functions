"""Type definitions for JSON data."""
JsonType = int | float | str | bool | list["JsonType"] | dict[str, "JsonType"] | None
