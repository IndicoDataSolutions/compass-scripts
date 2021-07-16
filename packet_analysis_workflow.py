"""
Script to run the full Indico workflow to split packets
and detect signatures. Note that all outputs from this
script will be saved to /path/to/packets/indico

Disclaimer: This is a proof of concept workflow and is split 
up into parts to make it easier to understand. In
production final results will be provided by a single
API call to a custom Indico Workflow that lives on the
Compass Indico Platform
"""
import sys
import os
from pathlib import Path

from doc_extraction import generate_ocr_output
from predictions import generate_prediction_output
from results import generate_final_output

import config

USAGE_STRING = "python packet_analysis_workflow.py /path/to/packets"


def analyze_packets():
    packet_dir = get_folder_from_args(sys.argv)
    if not packet_dir:
        sys.exit()

    initialize_workflow_directories(packet_dir)
    print("Starting OCR")
    generate_ocr_output(packet_dir)
    print("Completed OCR")

    print("Starting Predictions")
    generate_prediction_output(packet_dir)
    print("Completed Predictions")

    print("Generating Final Output")
    generate_final_output(packet_dir)
    print("Finished Final Output")


def get_folder_from_args(args):
    if len(args) != 2:
        print(USAGE_STRING)
        return None

    packet_dir = Path(args[1])
    if not packet_dir.is_dir():
        print(f"{packet_dir} is not a directory")
        return None

    if not packet_dir.exists():
        print(f"{packet_dir} does not exist")
        return None

    return packet_dir


def initialize_workflow_directories(packet_dir):
    first_level_dirs = [config.OCR_DIR, config.PREDICTION_DIR, config.RESULTS_DIR]
    for first_level_dir in first_level_dirs:
        create_output_dir(packet_dir, first_level_dir)

    prediction_dirs = [
        config.CLASSIFICATION_DIR,
        config.EXTRACTION_DIR,
        config.OBJECT_DETECTION_DIR,
    ]
    for prediction_dir in prediction_dirs:
        create_output_dir(packet_dir, prediction_dir)

    classification_dirs = [config.FIRST_PAGE_CLASSIFICATION_DIR, config.DOC_TYPE_CLASSIFICATION_DIR]
    for classification_dir in classification_dirs:
        create_output_dir(packet_dir, classification_dir)


def create_output_dir(packet_dir, output_dir):
    new_dir = os.path.join(packet_dir, output_dir)
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)


if __name__ == "__main__":
    analyze_packets()
