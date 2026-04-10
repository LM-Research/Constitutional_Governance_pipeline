from __future__ import annotations

import re
import yaml

__all__ = ["SpecViolation", "load_spec", "interpret"]


class SpecViolation(Exception):
    pass


def load_spec(path: str = "sl_spec.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def interpret(sl_spec: dict, raw_text: str) -> dict[str, str | None]:
    rel: dict[str, str | None] = {}
    for rule in sl_spec["rules"]:
        name: str = rule["name"]
        pattern: str = rule["pattern"]
        required: bool = rule.get("required", False)
        default: str | None = rule.get("default")
        match = re.search(pattern, raw_text)
        if not match:
            if required:
                raise SpecViolation(f"Missing required field: {name}")
            rel[name] = default
        else:
            rel[name] = match.group(1)
    return rel
