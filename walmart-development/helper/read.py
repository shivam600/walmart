import json
from pathlib import Path


def read_project_file(path):
    """
    Read a JavaScript file containing a JSON array.
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    text = path.read_text(encoding="utf-8")

    # Extract JSON array
    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1:
        raise ValueError(f"Could not find JSON array in {path}")

    return json.loads(text[start:end + 1])