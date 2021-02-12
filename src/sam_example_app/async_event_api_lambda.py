import json
import os

from aws_lambda_powertools import Tracer, Logger

from sam_example_app.lambda_lib.lambda_handler_decorators import rest_api_handler
from sam_example_app.lambda_lib.lmbda import async_invoke

logger = Logger()
xray_tracer = Tracer()


@xray_tracer.capture_lambda_handler
@rest_api_handler
def handler(event, *_):
    logger.info({"message": "Received Json from API GW", "event": event})
    lambda_name = os.environ.get("ASYNC_HANDLER_FN", "ASYNC_HANDLER_FN_NOT_SET")
    async_invoke(lambda_name, json.dumps(event), compress=True)
    return {"message": f"async invoked lambda {lambda_name}"}
