import json
from typing import Any


def maybe_json_dumps(value: Any) -> str | None:
    """Сериализует объект в JSON-строку для передачи в PostgreSQL jsonb."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, default=str)


def maybe_json_loads(value: Any) -> Any:
    """Десериализует JSON-строку из PostgreSQL в Python-объект."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    return value
