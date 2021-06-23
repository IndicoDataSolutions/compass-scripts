import pandas as pd
import re
import os
from collections import defaultdict

import config
from utils import save_json

DOC_START_COL = "Document Start Page"
PROPERTY_NAME_COL = "Property Name"
BUNDLE_PAGE_COL = "Bundle Page Number"


def generate_page_range_output(packet_dir):
    model_results_filepath = os.path.join(packet_dir, config.MODEL_RESULTS_FILEPATH)
    result_filepath = os.path.join(packet_dir, config.FINAL_RESULTS_FILEPATH)

    blind_test_df = pd.read_csv(model_results_filepath)
    blind_test_df["Predicted Page Number"] = (
        blind_test_df["Predicted Page Number"].fillna("").apply(extract_page_number)
    )
    properties = pd.unique(blind_test_df[PROPERTY_NAME_COL]).tolist()
    page_ranges = compute_page_ranges(blind_test_df, properties)
    save_json(page_ranges, result_filepath)


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
    page_range_dict = defaultdict(dict)
    blind_test_df.set_index(PROPERTY_NAME_COL, inplace=True)
    for property_name in properties:
        property_df = blind_test_df.loc[property_name]
        page_range_dict[property_name]["blind test"] = get_page_range(
            property_df, DOC_START_COL
        )
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


if __name__ == "__main__":
    packet_dir = "/home/ubuntu/Documents/compass-poc/blind_test/compass_scripts/data"
    generate_page_range_output(packet_dir)
