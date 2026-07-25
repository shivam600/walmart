import json
from pathlib import Path


def save_json_output(data, filename=None):
    """Save JSON data to output_files/output.json by default."""
    if filename is None:
        filename = Path(__file__).resolve().parents[1] / "output_files" / "output.json"
    else:
        filename = Path(filename)

    filename.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as output_file:
        json.dump(data, output_file, indent=2, ensure_ascii=False)

    return str(filename)


def load_json_output(filename=None):
    """Load JSON data from any file path."""
    if filename is None:
        filename = Path(__file__).resolve().parents[1] / "output_files" / "output.json"
    else:
        filename = Path(filename)

    with open(filename, "r", encoding="utf-8") as input_file:
        return json.load(input_file)
