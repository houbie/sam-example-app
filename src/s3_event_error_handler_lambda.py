from aws_lambda_powertools import Tracer, Logger

from lambda_lib.lmbda import async_invoke
from lambda_lib.s3 import move

MAX_RETRIES = 1

logger = Logger()
tracer = Tracer()


@tracer.capture_lambda_handler
def handler(event, context):
    logger.info({"message": "lambda failure event received", "event": event})
    request_payload = event["requestPayload"]
    retry_count = request_payload.get("retryCount", 0)
    if retry_count < MAX_RETRIES and event["responsePayload"]["errorType"] == "TimeoutError":
        logger.info({"message": f"retrying event after {retry_count} retries", "event": event})
        request_payload["retryCount"] = retry_count + 1
        async_invoke(event["requestContext"]["functionArn"], request_payload)
    else:
        for record in request_payload["Records"]:
            logger.info({"message": f"moving record after {retry_count} retries to error folder", "event": event})
            move(record["s3"]["bucket"]["name"], record["s3"]["object"]["key"], "error")
