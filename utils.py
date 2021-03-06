import json
import glob
import os
import pandas as pd

from indico_toolkit.ocr import OnDoc


def save_json(indico_obj, filepath):
    indico_string = json.dumps(indico_obj)
    with open(filepath, "w") as f:
        f.write(indico_string)


def get_filepaths_from_folder(path, ext):
    ext_regex = f"*.{ext}"
    filepaths = path.glob(ext_regex)
    return filepaths


def initialize_csv(columns, filepath):
    df = pd.DataFrame({}, columns=columns)
    df.to_csv(filepath, index=False)


def open_ocr(ocr_filepath):
    ocr_obj = open_json(ocr_filepath)
    ondoc_ocr = OnDoc(ocr_obj)
    return ondoc_ocr


def open_json(json_filepath):
    with open(json_filepath) as f:
        json_obj = json.load(f)
    return json_obj


def prediction_list_to_json(results_list):
    return [json.dumps(x) for x in results_list]


def get_property_names(filename_col):
    property_names = []
    for filepath in filename_col.tolist():
        filename = os.path.basename(filepath)
        property_name = filename.replace(".pdf.json", "")
        property_names.append(property_name)
    return property_names


def save_predictions(results, ocr_filepath, output_dir):
    filename = os.path.basename(ocr_filepath)
    output_filepath = os.path.join(output_dir, filename)
    save_json(results, output_filepath)
