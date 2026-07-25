from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.csv_reader import csv_reader_spreadsheet, save_js_output


REQUIRED_COLUMNS = [
    "level_4",
    "attribute",
    "requirement_level",
    "conditional_requirement",
    "acceptable_values",
    "example_values",
    "closed_list",
    "multiselect",
    "operations_direction",
    "acceptable_units",
    "acceptable_units_original",
    "minimum_required_entries",
    "recommended_no_of_entries",
    "min_word_count",
    "recommended_word_length",
    "definition",
    "min_char",
    "max_char",
    "precision",
    "display_name",
    "schema_key",
    "validation_instructions",
    "data_type",
    "destination_transformations_1",
]


def filter_project_type(project_type_name, pt_data):
    if not pt_data:
        return []

    header = pt_data[0]

    # Find indices of required columns
    column_indices = [
        header.index(col)
        for col in REQUIRED_COLUMNS
        if col in header
    ]

    # Find level_4 column index
    level4_idx = header.index("level_4")

    result = []

    # Filtered header
    result.append([header[i] for i in column_indices])

    # Filter rows
    for row in pt_data[1:]:
        if row[level4_idx] == project_type_name:
            result.append([row[i] for i in column_indices])

    return result


#if __name__ == "__main__":
    pt_url = "https://docs.google.com/spreadsheets/d/17IcL2aWI9kGmbkE16X1InDKU-ouBay3NtXnZoNWRH5s/export?format=csv&gid=1793441673"

    pt_data = csv_reader_spreadsheet(pt_url)

    project_type_name = "Speaker Mounts & Brackets"

    result = filter_project_type(project_type_name, pt_data)

    print(f"Filtered data for '{project_type_name}': {len(result)-1} rows")

    save_js_output(result, "output_files/project_type.js")