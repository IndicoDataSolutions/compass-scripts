import time
import os
import json
import pandas as pd
from tqdm import tqdm


import config
from indico_functions import predict, create_client
from utils import (
    save_json,
    initialize_csv,
    get_filepaths_from_folder,
    open_ocr,
    prediction_list_to_json,
    get_property_names,
    save_predictions
)


def get_extraction_results(packet_dir):
    INDICO_CLIENT = create_client(config.HOST, config.API_TOKEN_PATH)
    ocr_dir = os.path.join(packet_dir, config.OCR_DIR)
    extraction_dir = os.path.join(packet_dir, config.EXTRACTION_DIR)
    extractions_filepath = os.path.join(
        packet_dir, config.EXTRACTION_PREDICTIONS_CSV_PATH
    )

    initialize_csv(config.EXTRACTION_COLUMNS, extractions_filepath)
    ocr_filepaths = get_filepaths_from_folder(ocr_dir, "json")

    for ocr_filepath in tqdm(ocr_filepaths):

        ocr = open_ocr(ocr_filepath)
        page_texts = ocr.page_texts
        ocr_tokens = [[x] for x in ocr.token_objects]

        extraction_results = predict(
            INDICO_CLIENT, config.EXTRACTION_MODEL_ID, page_texts
        )
        save_predictions(extraction_results, ocr_filepath, extraction_dir)

        extraction_df = extraction_results_to_df(ocr_filepath, extraction_results)
        extraction_df.to_csv(extractions_filepath, header=False, mode="a", index=False)


def extraction_results_to_df(filepaths, extraction_results):
    extraction_jsons = prediction_list_to_json(extraction_results)
    filepaths_col = [filepaths] * len(extraction_jsons)
    page_numbers = range(1, len(extraction_jsons) + 1)
    df = pd.DataFrame(
        {
            "filename": filepaths_col,
            "page number": page_numbers,
            "extractions": extraction_jsons,
        }
    )

    formatted_df = format_extractions_df(df)
    return formatted_df


def format_extractions_df(extractions_df):
    property_names = get_property_names(extractions_df["filename"])
    doc_type_headers, doc_type_headers_confs = get_headers(extractions_df)
    page_numbers, page_numbers_confs = get_page_numbers(extractions_df)
    extraction_dict = {
        "Property Name": property_names,
        "Bundle Page Number": extractions_df["page number"],
        "Doc Type Header Predictions": doc_type_headers,
        "Doc Type Header Confidence": doc_type_headers_confs,
        "Predicted Page Number Text": page_numbers,
        "Predicted Page Number Confidence": page_numbers_confs,
    }
    extraction_results_df = pd.DataFrame(extraction_dict)
    return extraction_results_df


def get_headers(extraction_df):
    doc_type_headers = []
    doc_type_header_confs = []
    for _, row in extraction_df.iterrows():
        predictions = json.loads(row["extractions"])
        header_preds = [pred for pred in predictions if pred["label"] != "Page Number"]
        confs = [pred["confidence"][pred["label"]] for pred in header_preds]
        if confs:
            most_confident_ind = confs.index(max(confs))
            doc_type_headers.append(header_preds[most_confident_ind]["label"])
            doc_type_header_confs.append(confs[most_confident_ind])
        else:
            doc_type_headers.append(None)
            doc_type_header_confs.append(None)
    return doc_type_headers, doc_type_header_confs


def get_page_numbers(extraction_df):
    """Get Page Numbers for predictions"""
    page_numbers = []
    page_number_confs = []
    for _, row in extraction_df.iterrows():
        predictions = json.loads(row["extractions"])
        header_preds = [pred for pred in predictions if pred["label"] == "Page Number"]
        confs = [pred["confidence"][pred["label"]] for pred in header_preds]
        if confs:
            most_confident_ind = confs.index(max(confs))
            page_numbers.append(header_preds[most_confident_ind]["text"])
            page_number_confs.append(confs[most_confident_ind])
        else:
            page_numbers.append(None)
            page_number_confs.append(None)
    return page_numbers, page_number_confs


def apply_page_number(prediction_df, ocr_tokens):
    
    full_dfs = []
    for i, row in prediction_df.iterrows():
        prediction_string = row["extractions"]
        filename = row["filename"]
        predictions = json.loads(prediction_string)
        position_preds = create_bounded_preds(
            predictions, ocr_tokens[i], offset="page_offset"
        )
        page_pred_df = page_preds_to_df(filename, position_preds)
        full_dfs.append(page_pred_df)
    output_df = pd.concat(full_dfs)
    return output_df


def create_bounded_preds(doc_predictions, ocr_tokens):
    # ocr_tokens = ocr.token_objects
    line_item_fields = list(doc_predictions[0]["confidence"].keys())
    predictions = LineItems(doc_predictions, line_item_fields=line_item_fields)
    predictions.get_bounding_boxes(ocr_tokens)
    bounded_predictions = predictions.updated_predictions.to_list()
    return bounded_predictions


def page_preds_to_df(filename, position_preds):
    page_dict = defaultdict(list)
    for pred in position_preds:
        page_num = pred["page_num"] + 1
        page_dict[page_num].append(pred)

    df_dict = defaultdict(list)
    for page, preds in page_dict.items():
        df_dict["filename"].append(filename)
        df_dict["page number"].append(page)
        df_dict["extractions"].append(json.dumps(preds))

    df = pd.DataFrame(df_dict)
    return df


if __name__ == "__main__":
    packet_dir = "/home/ubuntu/Documents/compass-poc/blind_test/compass_scripts/data/"
    get_extraction_results(packet_dir)
