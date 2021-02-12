import os

from aws_lambda_powertools import Logger
from opentelemetry.trace import SpanKind

from sam_example_app.lambda_lib.power_requests import http
from sam_example_app.lambda_lib.tracing import tracer

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
    with tracer.start_as_current_span("child-span", kind=SpanKind.CLIENT) as span:
        span.name = "invoke event consumer"
        http.post(url, json=transformed)
    return "Successfully processed event"


def transform(event):
    return {key.upper(): value for key, value in event.items()}
