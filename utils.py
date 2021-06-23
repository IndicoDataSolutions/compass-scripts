import json
import glob
import os
import pandas as pd

from indico_toolkit.ocr import OnDoc


def save_json(indico_obj, filepath):
    indico_string = json.dumps(indico_obj)
    with open(filepath, "w") as f:
        f.write(indico_string)


def get_filepaths_from_folder(folder, ext):
    filepath_regex = os.path.join(folder, f"*.{ext}")
    filepaths = glob.glob(filepath_regex)
    return filepaths


def initialize_csv(columns, filepath):
    df = pd.DataFrame({}, columns=columns)
    df.to_csv(filepath, index=False)


def open_ocr(ocr_filepath):
    with open(ocr_filepath) as f:
        ocr_obj = json.load(f)
    ondoc_ocr = OnDoc(ocr_obj)
    return ondoc_ocr


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