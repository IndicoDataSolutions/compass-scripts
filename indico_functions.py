import time

from indico import IndicoClient, IndicoConfig
from indico.queries import (
    RetrieveStorageObject,
    ModelGroupPredict,
    JobStatus,
    DocumentExtraction,
)
from indico_toolkit.ocr import OnDoc

import config

def create_client(host, api_token_path):
    my_config = IndicoConfig(host=host, api_token_path=api_token_path)
    client = IndicoClient(config=my_config)
    return client


def indico_document_extraction(indico_client, packet_filepaths):
    # Send files to indico for OCR
    jobs = indico_client.call(
        DocumentExtraction(packet_filepaths, json_config=config.OCR_CONFIG)
    )
    doc_extractions = []

    # NOTE: this can be sped up with parallelization
    for job in jobs:
        # wait for OCR jobs to complete and get results
        job_status = indico_client.call(JobStatus(id=job.id, wait=True))
        if job_status.status == "SUCCESS":
            # job_status contains a url where you can download ocr output
            storage_url = job_status.result
            # Checkout utils for implementation
            # Also used to get prediction results
            result = get_storage_object(indico_client, storage_url)
            doc_extractions.append(result)
        else:
            doc_extractions.append([])
    return doc_extractions


def get_storage_object(indico_client, storage_url, n_retries=3, cooldown=3):
    try:
        # download result object from indico
        result = indico_client.call(RetrieveStorageObject(storage_url))
        return result
    except Exception as e:
        if n_retries == 0:
            return []
        else:
            time.sleep(cooldown)
            return get_storage_object(
                indico_client, storage_url, n_retries - 1, cooldown=cooldown
            )


def predict(indico_client, model_id, data, **kwargs):
    # submit Document Text to indico for prediction
    job = indico_client.call(
        ModelGroupPredict(model_id=model_id, data=data, **kwargs)
    )
    results = get_prediction_results(indico_client, job)
    if results:
        return results
    else:
        print("broken preds beware")
        return [{} for x in range(len(data))]


def get_prediction_results(indico_client, job, n_retries=3, cooldown=5):
    try:
        job_status = indico_client.call(JobStatus(id=job.id, wait=True))
        results = job_status.result
        if isinstance(results, dict):
            if n_retries > 0:
                time.sleep(cooldown)
                return predict(
                    client, model_id, filenames, n_retries - 1, cooldown=cooldown
                )
            else:
                return None
        else:
            return results
    except:
        if n_retries > 0:
            time.sleep(cooldown)
            return predict(
                indico_client, model_id, filenames, n_retries - 1, cooldown=cooldown
            )
        else:
            return None


