from aws_lambda_powertools import Tracer, Logger

from event_handler import process_event
from lambda_lib.lambda_handler_decorators import s3_json_event_handler

logger = Logger()
tracer = Tracer()


@tracer.capture_lambda_handler
@s3_json_event_handler
def handler(event):
    logger.info({"message": "Received Json from S3"})
    return process_event(event)
