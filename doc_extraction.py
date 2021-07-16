import os
import sys
from tqdm import tqdm
from pathlib import Path
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

USAGE_STRING = "python3 doc_extraction.py <directory_with_docs>"


def generate_ocr_output(packet_dir, overwrite=False, **kwargs):
    INDICO_CLIENT = create_client(config.HOST, config.API_TOKEN_PATH)
    ocr_dir = packet_dir / config.OCR_DIR

    packet_filepaths = get_filepaths_from_folder(packet_dir, "pdf")
    if not overwrite:
        packet_filepaths = [
            p            
            for p in packet_filepaths 
            if not (ocr_dir / (p.name + ".json")).exists()
        ]
    else:
        packet_filepaths = list(packet_filepaths)

    batch_size = 6
    for batch_start in tqdm(range(0,len(packet_filepaths), batch_size)):
        batch_end = batch_start + batch_size
        batch_filepaths = packet_filepaths[batch_start:batch_end]
        ocr_extractions = indico_document_extraction(INDICO_CLIENT, batch_filepaths, **kwargs)
        save_ocr_data(ocr_extractions, batch_filepaths, ocr_dir)


def save_ocr_data(ocr_extractions, packet_filepaths, output_dir):
    for ocr_extraction, packet_filepath in zip(ocr_extractions, packet_filepaths):
        filename = os.path.basename(packet_filepath)
        output_filepath = os.path.join(output_dir, f"{filename}.json")
        save_json(ocr_extraction, output_filepath)


def doc_extraction():
    if len(sys.argv) < 2:
        print(USAGE_STRING)
        sys.exit()
    document_dir = Path(sys.argv[1])
    output_dir = document_dir / config.OCR_DIR

    if not output_dir.exists():
        os.mkdir(output_dir)
    
    
    ocr_config = {"preset_config": "simple"}
    generate_ocr_output(document_dir, ocr_config=ocr_config)
    
if __name__ == "__main__":
    # packet_dir = "/home/ubuntu/Documents/compass-poc/blind_test/compass_scripts/data/"
    doc_extraction()
