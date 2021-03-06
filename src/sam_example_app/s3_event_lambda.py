from aws_lambda_powertools import Tracer, Logger

from sam_example_app.event_handler import process_event
from sam_example_app.lambda_lib.lambda_handler_decorators import s3_json_event_handler

logger = Logger()
xray_tracer = Tracer()


@xray_tracer.capture_lambda_handler
@s3_json_event_handler("sam-example-s3-flow", functional_key=("name", "name"))
def handler(json_body, *_):
    logger.info({"message": "Received Json from S3"})
    return process_event(json_body)
