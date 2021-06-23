import os


HOST = "poc-compass.indico.domains"
API_TOKEN_PATH = "/home/ubuntu/Documents/compass-poc/indico_api_token.txt"

OCR_DIR = "ocr"
PREDICTION_DIR = "predictions"
RESULTS_DIR = "results"

CLASSIFICATION_DIR = os.path.join(PREDICTION_DIR, "classifications")
FIRST_PAGE_CLASSIFICATION_DIR = os.path.join(
    CLASSIFICATION_DIR, "first_page_classifications"
)
DOC_TYPE_CLASSIFICATION_DIR = os.path.join(
    CLASSIFICATION_DIR, "doc_type_page_classifications"
)
CLASSIFICATION_FILEPATH = os.path.join(CLASSIFICATION_DIR, "classification.csv")

EXTRACTION_DIR = os.path.join(PREDICTION_DIR, "extractions")
EXTRACTION_PREDICTIONS_CSV_PATH = os.path.join(
    EXTRACTION_DIR, "extraction_results.csv"
)

OBJECT_DETECTION_DIR = os.path.join(PREDICTION_DIR, "signature_detections")
OBJ_DETECT_RESULTS_CSV_PATH = os.path.join(OBJECT_DETECTION_DIR, "signature_detection.csv")

MODEL_RESULTS_FILEPATH = os.path.join(RESULTS_DIR, "model_results.csv")

PAGE_RANGES_FILEPATH = os.path.join(RESULTS_DIR, "page_ranges.json")
FINAL_RESULTS_FILEPATH = os.path.join(RESULTS_DIR, "final_output.json")

OCR_CONFIG = {"preset_config": "ondocument"}

SIGNATURE_ONLY_MODEL_ID = 51
EXTRACTION_MODEL_ID = 58
FIRST_PAGE_MODEL_ID = 12
DOC_TYPE_MODEL_ID = 60
PREDICT_THRESHOLD = 0.65

CLASSIFIER_COLUMNS = [
    "Property Name",
    "Bundle Page Number",
    "First Page Classification Predictions",
    "First Page Classification Confidence",
    "Document Type Classification Prediction",
    "Document Type Classification Confidence",
]
EXTRACTION_COLUMNS = [
    "Property Name",
    "Bundle Page Number",
    "Doc Type Header Predictions",
    "Doc Type Header Confidence",
    "Predicted Page Number",
    "Predicted Page Number Confidence",
]
FINAL_COLUMN_ORDER = [
    "Platform",
    "Region",
    "Property Name",
    "Bundle Page Number",
    "Original Filename",
    "SkySlope File Name",
    "Page Range",
    "First Page Classification Predictions",
    "First Page Classification Confidence",
    "Document Type Classification Prediction",
    "Document Type Classification Confidence",
    "Doc Type Header Predictions",
    "Doc Type Header Confidence",
    "Document Page Number",
    "Predicted Page Number",
    "Predicted Page Number Confidence",
    "# of Signatures",
    "# of Predicted Signatures",
    "Signature Confidences",
]
