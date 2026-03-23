import re
import yaml

class SpecViolation(Exception):
    pass

def load_spec(path="sl_spec.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def interpret(sl_spec, raw_text):
    rel = {}

    for rule in sl_spec["rules"]:
        name = rule["name"]
        pattern = rule["pattern"]
        required = rule.get("required", False)
        default = rule.get("default")

        match = re.search(pattern, raw_text)
        if not match:
            if required:
                raise SpecViolation(f"Missing required field: {name}")
            rel[name] = default
        else:
            rel[name] = match.group(1)

    return rel
