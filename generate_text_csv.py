import pandas as pd
import json
import sys
from pathlib import Path
from collections import defaultdict


from utils import open_json


USAGE_STRING = "python3 generate_text_csv.py <path_to_ocr_files>"
COLUMNS = ["Filename", "Page Number", "Page Text"]

def generate_csv():
    if len(sys.argv) < 2:
        print(USAGE_STRING)
        sys.exit()
    
    ocr_dir = Path(sys.argv[1])
    ocr_filepaths = ocr_dir.glob("*.json")
    
    
    doc_dict = defaultdict(list)

    for ocr_filepath in ocr_filepaths:

        ocr_obj = open_json(ocr_filepath)

        for page_num, page in enumerate(ocr_obj):
            doc_dict["Filename"].append(ocr_filepath)
            doc_dict["Page Number"].append(page_num + 1)
            doc_dict["Page Text"].append(page["pages"][0]["text"])
        
    page_text_df = pd.DataFrame(doc_dict)
    output_file = ocr_dir / "page_text.csv"
    page_text_df.to_csv(output_file, index=False)

if __name__ == "__main__":
    generate_csv()
            
          
        

