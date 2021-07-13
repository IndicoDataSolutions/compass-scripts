import os
import sys
from tqdm import tqdm

from utils import (
    save_json,
    get_filepaths_from_folder,
)
from indico_functions import (
    create_client,
    indico_document_extraction,
    get_storage_object,
)

import config

from indico.queries import DocumentExtraction, JobStatus


def generate_ocr_output(packet_dir):
    INDICO_CLIENT = create_client(config.HOST, config.API_TOKEN_PATH)
    packet_filepaths = get_filepaths_from_folder(packet_dir, "pdf")
    batch_size = 6
    for batch_start in tqdm(range(0,len(packet_filepaths), batch_size)):
        batch_end = batch_start + batch_size
        batch_filepaths = packet_filepaths[batch_start:batch_end]
        ocr_extractions = indico_document_extraction(INDICO_CLIENT, batch_filepaths)
        save_ocr_data(ocr_extractions, batch_filepaths, packet_dir)


def save_ocr_data(ocr_extractions, packet_filepaths, packet_dir):
    output_dir = os.path.join(packet_dir, config.OCR_DIR)
    for ocr_extraction, packet_filepath in zip(ocr_extractions, packet_filepaths):
        filename = os.path.basename(packet_filepath)
        output_filepath = os.path.join(output_dir, f"{filename}.json")
        save_json(ocr_extraction, output_filepath)


if __name__ == "__main__":
    # packet_dir = sys.argv[1]
    packet_dir = "/home/ubuntu/Documents/compass-poc/blind_test/compass_scripts/data/"
    generate_ocr_output(packet_dir)
