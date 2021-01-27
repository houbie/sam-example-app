import os

from aws_lambda_powertools import Logger

from lambda_lib.power_requests import http

logger = Logger()


def process_event(event):
    logger.info({"message": "process_event", "event": event})
    # force some exceptions based on the event content
    if "panic" in event:
        logger.error({"message": "panic!!"})
        raise RuntimeError("received panic event!!!")
    if "pleaseRetry" in event:
        logger.error({"message": "pleaseRetry event received"})
        raise TimeoutError("received pleaseRetry event")

    transformed = transform(event)
    url = os.environ.get("EVENT_CONSUMER_URL", "EVENT_CONSUMER_URL_NOT_SET")
    logger.debug({"message": f"POST event to {url}", "event": event})
    http.post(url, json=transformed)
    return "Successfully processed event"


def transform(event):
    return {key.upper(): value for key, value in event.items()}
