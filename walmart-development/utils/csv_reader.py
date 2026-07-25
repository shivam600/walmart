import csv
import json
import requests
from io import StringIO
from pathlib import Path

def csv_reader_spreadsheet(url):

    response = requests.get(url)
    response.raise_for_status()

    reader = csv.reader(StringIO(response.text))
    data = list(reader)
    return data


def save_js_output(data, filename=None):
    if filename is None:
        filename = Path(__file__).resolve().parents[1] / "output_files" / "output.js"
    else:
        filename = Path(filename)

    filename.parent.mkdir(parents=True, exist_ok=True)
    js_content = "const outputData = " + json.dumps(data, indent=2) + ";\n"
    js_content += "export default outputData;\n"

    with open(filename, "w", encoding="utf-8") as output_file:
        output_file.write(js_content)

    return str(filename)

def filter_json_data(json_data):
    # remove all the empty key value pairs from this
    filtered_data = []
    for row in json_data:
        filtered_row = {k: v for k, v in row.items() if v}
        if filtered_row:
            filtered_data.append(filtered_row)
    return filtered_data

def convert_to_json(data):
    if not data:
        return []

    headers = [header.strip() for header in data[0]]
    json_rows = []

    for row in data[1:]:
        row_values = [value.strip() for value in row]
        row_values += [""] * max(0, len(headers) - len(row_values))
        row_obj = {headers[i]: row_values[i] for i in range(len(headers))}
        json_rows.append(row_obj)

    return json_rows


def csv_reader(url):
    data = csv_reader_spreadsheet(url)
    json_data = convert_to_json(data)
    filtered_json_data = filter_json_data(json_data)
    output_path = save_js_output(filtered_json_data)
    return filtered_json_data


# if __name__ == "__main__":
    # url = "https://docs.google.com/spreadsheets/d/17IcL2aWI9kGmbkE16X1InDKU-ouBay3NtXnZoNWRH5s/export?format=csv&gid=1793441673"
    # url = "https://docs.google.com/spreadsheets/d/1_-O6blSniTTsEVXlliykf46s_ulrTR-4zTjwI8OQIrA/export?format=csv&gid=691326073"
    # csv_reader(url)