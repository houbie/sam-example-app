from aws_lambda_powertools import Tracer, Logger

from lambda_lib.lambda_handler_decorators import rest_api_handler

logger = Logger()
tracer = Tracer()


@tracer.capture_lambda_handler
@rest_api_handler
def handler(event):
    logger.info({"message": "Consuming event", "event": event})
    return {"message": "consumed event"}
