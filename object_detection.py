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


def object_detection_predictions(packet_dir):
    INDICO_CLIENT = create_client(config.HOST, config.API_TOKEN_PATH)
    ocr_dir = os.path.join(packet_dir, config.OCR_DIR)
    signature_dir = os.path.join(packet_dir, config.OBJECT_DETECTION_DIR)
    signature_csv_filepath = os.path.join(packet_dir, config.OBJ_DETECT_RESULTS_CSV_PATH)
    ocr_filepaths = get_filepaths_from_folder(ocr_dir, "json")
    pred_dfs = []

    for ocr_filepath in ocr_filepaths:
        storage_df = get_storage_urls(ocr_filepath)
        batch_size = 100
        for batch_start in tqdm(range(0, storage_df.shape[0], batch_size)):
            batch_end = batch_start + batch_size - 1
            storage_batch_df = storage_df.loc[batch_start:batch_end]
            storage_urls = storage_batch_df["storage_urls"].tolist()
            predictions = predict(
                INDICO_CLIENT,
                config.SIGNATURE_ONLY_MODEL_ID,
                storage_urls,
                load=False,
            )
            save_predictions(predictions, ocr_filepath, signature_dir)
            storage_batch_df["predictions"] = predictions
            formatted_df = format_obj_detection_df(storage_batch_df)
            pred_dfs.append(formatted_df)
    full_df = pd.concat(pred_dfs)
    full_df.to_csv(signature_csv_filepath, index=False)


def get_storage_urls(ocr_filepath):
    page_nums = []
    storage_urls = []
    filenames = []    
    ocr = open_ocr(ocr_filepath)
    filename = os.path.basename(ocr_filepath)
    for page_num, page in enumerate(ocr.ondoc):
        storage_urls.append(page["pages"][0]["image"]["url"])
        filenames.append(filename)
        page_nums.append(page_num+1)
    storage_dict = {
        "filename": filenames,
        "page number": page_nums,
        "storage_urls": storage_urls,
    }
    return pd.DataFrame(storage_dict)

def format_obj_detection_df(sig_detection_df):
    property_names = [
        x.replace(".pdf.json", "") for x in sig_detection_df["filename"].tolist()
    ]
    signature_counts, sig_counts_confs = get_signature_counts(sig_detection_df)
    obj_detection_dict = {
        "Property Name": property_names,
        "Bundle Page Number": sig_detection_df["page number"],
        "# of Predicted Signatures": signature_counts,
        "Signature Confidences": sig_counts_confs,
    }
    sig_detection_results_df = pd.DataFrame(obj_detection_dict)
    return sig_detection_results_df


def get_signature_counts(sig_detection_df):
    signature_counts = []
    sig_counts_confs = []
    for _, row in sig_detection_df.iterrows():
        predictions = row["predictions"]
        signatures = [pred for pred in predictions if pred["label"] == "Signed"]
        confidences = [
            pred["confidence"] for pred in signatures if pred["confidence"] > 0.65
        ]
        signature_counts.append(len(confidences))
        sig_counts_confs.append(json.dumps(confidences))
    return signature_counts, sig_counts_confs



if __name__ == "__main__":
    packet_dir = "/home/ubuntu/Documents/compass-poc/blind_test/compass_scripts/data/"
    object_detection_predictions(packet_dir)