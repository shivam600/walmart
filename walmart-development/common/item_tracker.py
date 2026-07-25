import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from helper.read import read_project_file
from helper.load_data import load_json_output, save_json_output


def load_project_data():
    """
    Load data from output_files/item_tracker.js
    """
    path = ROOT_DIR / "output_files" / "output.js"
    return read_project_file(path)


def item_tracker(item_data):
    """
    Group items by Product Type.
    """

    grouped = {}

    for item in item_data:
        product_type = item.get("Product Type")

        if not product_type:
            continue

        grouped.setdefault(product_type, []).append(item)

    return grouped

# if __name__ == "__main__":
#     item_data = load_project_data()
#     grouped = item_tracker(item_data)
#     save_json_output(grouped, filename="../output_files/item_tracker.js")
    # print(json.dumps(grouped, indent=2, ensure_ascii=False))