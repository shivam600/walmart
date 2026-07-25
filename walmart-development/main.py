from common.item_tracker import item_tracker
from utils.csv_reader import csv_reader , csv_reader_spreadsheet
from common.project_type import filter_project_type
from utils.gemini_prompt import gemini_prompt_validation
from helper.load_data import save_json_output
from utils.validation import load_sop_from_url

def save_response(response, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(response))

def main():
    item_url = "https://docs.google.com/spreadsheets/d/1_-O6blSniTTsEVXlliykf46s_ulrTR-4zTjwI8OQIrA/export?format=csv&gid=691326073"
    pt_url = "https://docs.google.com/spreadsheets/d/17IcL2aWI9kGmbkE16X1InDKU-ouBay3NtXnZoNWRH5s/export?format=csv&gid=1793441673"
    sop_url = "https://docs.google.com/document/d/1K_WDyvVW9gTdn1GEJ1ID485_Wvlh8BGA/export?format=docx"

    item_data = csv_reader(item_url)
    pt_data = csv_reader_spreadsheet(pt_url)
    print(pt_url)
    sop_data = load_sop_from_url(sop_url)

    filtered_item_data = item_tracker(item_data)

    limit = 1
    result = []
    offset = 0

    for key, value in filtered_item_data.items():
        attributes = filter_project_type(key, pt_data)

        vlen = len(value)
        while offset < vlen:
            input_data = value[offset:offset + limit]
            res = gemini_prompt_validation(input_data, attributes , sop_data)
            result.append(res)
            break
            offset += limit
        break
        offset = 0
    print(result)

    save_response(result, "output_files/result2.txt")

if __name__ == "__main__":
    main()