from classifications import get_classification_results
from extractions import get_extraction_results
from object_detection import object_detection_predictions


def generate_prediction_output(packet_dir):

    print("Starting Classifications")
    get_classification_results(packet_dir)
    print("Finished Classifications")

    print("Starting Extractions")
    get_extraction_results(packet_dir)
    print("Finished Extractions")

    print("Starting Object Detection")
    object_detection_predictions(packet_dir)
    print("Finished Object Detection")

if __name__ == "__main__":
    # packet_dir = sys.argv[1]
    packet_dir = "/home/ubuntu/Documents/compass-poc/blind_test/compass_scripts/data/"
    generate_prediction_output(packet_dir)