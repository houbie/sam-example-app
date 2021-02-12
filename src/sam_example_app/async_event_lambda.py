from aws_lambda_powertools import Tracer, Logger

from sam_example_app.event_handler import process_event
from sam_example_app.lambda_lib.lambda_handler_decorators import compressed_json_event_handler

logger = Logger()
xray_tracer = Tracer()


@xray_tracer.capture_lambda_handler
@compressed_json_event_handler
def handler(event, *_):
    logger.info({"message": "Received Json from Async invoke", "event": event})
    return process_event(event)
