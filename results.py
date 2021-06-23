import pandas as pd
import os

import config


def generate_model_results_csv(packet_dir):
    results_csv_filepath = os.path.join(packet_dir, config.MODEL_RESULTS_FILEPATH)
    classification_csv_filepath = os.path.join(
        packet_dir, config.CLASSIFICATION_FILEPATH
    )
    extraction_csv_filepath = os.path.join(
        packet_dir, config.EXTRACTION_PREDICTIONS_CSV_PATH
    )
    sig_detection_filepath = os.path.join(
        packet_dir, config.OBJ_DETECT_RESULTS_CSV_PATH
    )

    classification_df = pd.read_csv(classification_csv_filepath)
    extraction_df = pd.read_csv(extraction_csv_filepath)
    sig_detection_df = pd.read_csv(sig_detection_filepath)

    dfs = [classification_df, extraction_df, sig_detection_df]
    final_result_df = merge_results(dfs)
    final_result_df.to_csv(results_csv_filepath, index=False)


def merge_results(dfs):
    merged_df = dfs[0]
    for df in dfs[1:]:
        merged_df = merged_df.merge(
            df, on=["Property Name", "Bundle Page Number"], how="left"
        )
    return merged_df


if __name__ == "__main__":
    packet_dir = "/home/ubuntu/Documents/compass-poc/blind_test/compass_scripts/data/"
    generate_final_results(packet_dir)
