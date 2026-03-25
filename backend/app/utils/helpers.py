import re
from typing import Any


def safe_str(val: Any) -> str:
    if val is None:
        return ""
    return str(val).strip()


def truncate(text: str, max_len: int = 200) -> str:
    return text if len(text) <= max_len else text[:max_len] + "..."


def flatten_dict(d: dict, parent_key: str = "", sep: str = "_") -> dict:
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep))
        else:
            items[new_key] = v
    return items


def clean_sql(sql: str) -> str:
    sql = re.sub(r"```sql\s*", "", sql)
    sql = re.sub(r"```\s*", "", sql)
    sql = sql.strip().rstrip(";") + ";"
    return sql


def sanitize_identifier(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "_", name)
