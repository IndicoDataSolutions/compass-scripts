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
    save_predictions,
)


def get_classification_results(packet_dir):
    INDICO_CLIENT = create_client(config.HOST, config.API_TOKEN_PATH)
    ocr_dir = os.path.join(packet_dir, config.OCR_DIR)
    first_page_dir = os.path.join(packet_dir, config.FIRST_PAGE_CLASSIFICATION_DIR)
    doc_type_dir = os.path.join(packet_dir, config.DOC_TYPE_CLASSIFICATION_DIR)
    classifictions_filepath = os.path.join(packet_dir, config.CLASSIFICATION_FILEPATH)

    initialize_csv(config.CLASSIFIER_COLUMNS, classifictions_filepath)
    ocr_filepaths = get_filepaths_from_folder(ocr_dir, "json")

    for ocr_filepath in tqdm(ocr_filepaths):
        ocr = open_ocr(ocr_filepath)
        # check out indico_functions for specific indico calls
        first_page_results = predict(
            INDICO_CLIENT, config.FIRST_PAGE_MODEL_ID, ocr.page_texts
        )
        # Save Raw predictions
        save_predictions(first_page_results, ocr_filepath, first_page_dir)

        doc_type_results = predict(
            INDICO_CLIENT, config.DOC_TYPE_MODEL_ID, ocr.page_texts
        )
        save_predictions(doc_type_results, ocr_filepath, doc_type_dir)

        # Save Results to CSV
        classification_results_df = classification_results_to_df(
            [ocr_filepath], first_page_results, doc_type_results
        )

        classification_results_df.to_csv(
            classifictions_filepath, mode="a", index=False, header=False
        )


def classification_results_to_df(filepaths, first_page_results, doc_type_results):
    first_page_jsons = prediction_list_to_json(first_page_results)
    doc_type_jsons = prediction_list_to_json(doc_type_results)
    n_pages = len(first_page_results)
    pages = range(1, n_pages + 1)

    df_dict = {
        "filename": filepaths * n_pages,
        "page number": pages,
        "first page": first_page_jsons,
        "doc type": doc_type_jsons,
    }
    df = pd.DataFrame(df_dict)
    formatted_df = format_classification_df(df)
    return formatted_df


def format_classification_df(classifications_df):
    property_names = get_property_names(classifications_df["filename"])
    first_pages, first_page_confs = get_classifications(
        classifications_df, "first page"
    )
    doc_types, doc_types_confs = get_classifications(classifications_df, "doc type")
    classification_results_dict = {
        "Property Name": property_names,
        "Bundle Page Number": classifications_df["page number"],
        "First Page Classification Predictions": first_pages,
        "First Page Classification Confidence": first_page_confs,
        "Document Type Classification Prediction": doc_types,
        "Document Type Classification Confidence": doc_types_confs,
    }
    classification_results_df = pd.DataFrame(classification_results_dict)
    return classification_results_df


def get_classifications(classifications_df, column):
    pred_strings = classifications_df[column].to_list()
    results = []
    results_confs = []
    for pred_string in pred_strings:
        preds = json.loads(pred_string)
        result = max(preds, key=preds.get)
        confidence = max(preds.values())
        results.append(result)
        results_confs.append(confidence)
    return results, results_confs


if __name__ == "__main__":
    packet_dir = "/home/ubuntu/Documents/compass-poc/blind_test/compass_scripts/data/"
    get_classification_results(packet_dir)
