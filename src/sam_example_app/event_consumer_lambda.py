from aws_lambda_powertools import Tracer, Logger
from opentelemetry import trace

from sam_example_app.lambda_lib.lambda_handler_decorators import rest_api_handler

logger = Logger()
xray_tracer = Tracer()


@xray_tracer.capture_lambda_handler
@rest_api_handler
def handler(event, *_):
    trace.get_current_span().set_attribute("name", event.get("NAME", "no name provided"))
    logger.info({"message": "Consuming event", "event": event})
    return {"message": "consumed event"}
