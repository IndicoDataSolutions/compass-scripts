import pandas as pd
import re
import os
import json
from collections import defaultdict, Counter

import config
from utils import save_json

DOC_START_COL = "Document Start Page"
PROPERTY_NAME_COL = "Property Name"
BUNDLE_PAGE_COL = "Bundle Page Number"


def generate_page_range_output(packet_dir):
    model_results_filepath = os.path.join(packet_dir, config.MODEL_RESULTS_FILEPATH)

    blind_test_df = pd.read_csv(model_results_filepath)
    blind_test_df["Predicted Page Number"] = (
        blind_test_df["Predicted Page Number"].fillna("").apply(extract_page_number)
    )
    blind_test_df["Doc Type Header Confidence"] = blind_test_df[
        "Doc Type Header Confidence"
    ].fillna(0)
    properties = pd.unique(blind_test_df[PROPERTY_NAME_COL]).tolist()
    page_ranges = compute_page_ranges(blind_test_df, properties)
    classification_ranges = compute_classifiction_ranges(
        blind_test_df, properties, page_ranges
    )
    compute_signature_counts(blind_test_df, properties, page_ranges)
    return page_ranges


def extract_page_number(page_number_text):
    # grab first number
    regex = r"\d+"
    page_number_match = re.search(regex, page_number_text)
    if page_number_match:
        return int(page_number_match.group(0))


def compute_document_start_page(blind_test_df, properties):
    blind_test_df[DOC_START_COL] = None
    blind_test_df.set_index(PROPERTY_NAME_COL, inplace=True)
    for property_name in properties:
        blind_test_df.loc[property_name, DOC_START_COL] = get_document_start_pages(
            blind_test_df.loc[property_name, :]
        )
    blind_test_df.reset_index(inplace=True)
    return blind_test_df


def get_document_start_pages(property_df):
    first_page_mask = property_df["First Page Classification Predictions"] == True
    page_one_mask = property_df["Predicted Page Number"] == 1
    non_predicted_page_mask = property_df["Predicted Page Number"].isna()
    page_break_mask = first_page_mask & (page_one_mask | non_predicted_page_mask)
    return page_break_mask


def compute_page_ranges(blind_test_df, properties):
    blind_test_df = compute_document_start_page(blind_test_df, properties)
    page_range_dict = {}
    blind_test_df.set_index(PROPERTY_NAME_COL, inplace=True)
    for property_name in properties:
        property_df = blind_test_df.loc[property_name]
        page_range_dict[property_name] = get_page_range(property_df, DOC_START_COL)
    blind_test_df.reset_index(inplace=True)
    return page_range_dict


def get_page_range(property_df, page_col, match_criteria=True):
    page_ranges = []
    start_page = property_df[BUNDLE_PAGE_COL].iloc[0]
    end_page = start_page
    for row_num, (_, row) in enumerate(property_df.iterrows()):
        if is_start_page(row[page_col], match_criteria):
            start_page = row[BUNDLE_PAGE_COL]
            next_page = get_next_page(property_df, row_num, page_col)
            if is_last_page(row_num, property_df) or is_start_page(
                next_page, match_criteria
            ):
                end_page = row[BUNDLE_PAGE_COL]
                page_ranges.append(get_page_dict(start_page, end_page))
        else:
            end_page = row[BUNDLE_PAGE_COL]
            next_page = get_next_page(property_df, row_num, page_col)
            if is_last_page(row_num, property_df) or is_start_page(
                next_page, match_criteria
            ):
                page_ranges.append(get_page_dict(start_page, end_page))
    return page_ranges


def compute_classifiction_ranges(blind_test_df, properties, page_ranges):
    classification_range_dict = defaultdict(list)
    blind_test_df.set_index(PROPERTY_NAME_COL, inplace=True)
    for property_name in properties:
        property_df = blind_test_df.loc[property_name]
        add_classification_range(property_df, page_ranges[property_name])
    blind_test_df.reset_index(inplace=True)


def add_classification_range(property_df, page_ranges):
    bundle_df = property_df.reset_index().set_index(BUNDLE_PAGE_COL)
    for page_range in page_ranges:
        start = page_range["start"]
        end = page_range["end"]
        document_df = bundle_df.loc[start:end]
        most_conf_class, most_conf = get_most_confident_class(document_df)
        most_pop_class, most_pop_conf = get_most_popular_class(document_df)
        page_range.update(
            get_class_dict(most_conf_class, most_conf, most_pop_class, most_pop_conf)
        )


def get_most_confident_class(document_df):
    max_doc_type_class_idx = document_df[
        "Document Type Classification Confidence"
    ].idxmax()
    max_doc_type_header_idx = document_df["Doc Type Header Confidence"].idxmax()
    max_doc_type_class_conf = document_df[
        "Document Type Classification Confidence"
    ].loc[max_doc_type_class_idx]
    max_doc_type_header_conf = document_df["Doc Type Header Confidence"].loc[
        max_doc_type_header_idx
    ]
    conf_dict = {
        "Doc Type Header Predictions": max_doc_type_header_conf,
        "Document Type Classification Prediction": max_doc_type_class_conf,
    }
    idx_dict = {
        "Doc Type Header Predictions": max_doc_type_header_idx,
        "Document Type Classification Prediction": max_doc_type_class_idx,
    }

    max_conf_col = max(conf_dict, key=conf_dict.get)
    max_conf = max(conf_dict.values())
    max_class = document_df[max_conf_col].loc[idx_dict[max_conf_col]]
    return max_class, float(max_conf)


def get_most_popular_class(document_df):
    header_classes = document_df["Doc Type Header Predictions"].dropna().tolist()
    classifier_classes = (
        document_df["Document Type Classification Prediction"].dropna().tolist()
    )
    classes = header_classes + classifier_classes
    class_counts = Counter(classes)
    most_popular_class = max(class_counts, key=class_counts.get)

    most_popular_mask = document_df["Doc Type Header Predictions"] == most_popular_class
    header_confs = document_df["Doc Type Header Confidence"][most_popular_mask].tolist()

    most_popular_mask = (
        document_df["Document Type Classification Prediction"] == most_popular_class
    )
    classifier_confs = document_df["Document Type Classification Confidence"][
        most_popular_mask
    ].tolist()
    confs = header_confs + classifier_confs
    return most_popular_class, float(max(confs))


def compute_signature_counts(blind_test_df, properties, page_ranges):
    signature_dict = defaultdict(list)
    blind_test_df.set_index(PROPERTY_NAME_COL, inplace=True)
    for property_name in properties:
        property_df = blind_test_df.loc[property_name]
        add_signature_counts(property_df, page_ranges[property_name])
    blind_test_df.reset_index(inplace=True)


def add_signature_counts(property_df, page_ranges):
    bundle_df = property_df.reset_index().set_index(BUNDLE_PAGE_COL)
    for page_range in page_ranges:
        start = page_range["start"]
        end = page_range["end"]
        page_df = bundle_df.loc[start:end]
        n_signatures = page_df["# of Predicted Signatures"].sum(skipna=True)
        confs = []
        for conf in page_df["Signature Confidences"].fillna("[]"):
            confs.extend(json.loads(conf))
        map(float, confs)
        page_range.update(get_signature_dict(n_signatures, confs))


def is_last_page(row_num, property_df):
    return row_num == property_df.shape[0] - 1


def is_start_page(value, match_criteria):
    return value == match_criteria


def get_next_page(df, current_row, col):
    try:
        page_num = df.iloc[current_row + 1][col]
        return page_num
    except IndexError:
        return None


def get_page_dict(start_page, end_page):
    return {"start": int(start_page), "end": int(end_page)}


def get_class_dict(max_conf_class, max_conf, most_pop_class, most_pop_conf):
    class_dict = {
        "max confident class": max_conf_class,
        "max confident confidence": max_conf,
        "most popular class": most_pop_class,
        "most popular confidence": most_pop_conf,
    }
    return class_dict


def get_signature_dict(n_signatues, confidences):
    sig_dict = {"# signatures": int(n_signatues), "signature confidences": confidences}
    return sig_dict


if __name__ == "__main__":
    packet_dir = "/home/ubuntu/Documents/compass-poc/blind_test/compass_scripts/data"
    generate_page_range_output(packet_dir)
