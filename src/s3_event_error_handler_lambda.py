from aws_lambda_powertools import Tracer, Logger

from lambda_lib.lmbda import async_invoke
from lambda_lib.s3 import move
from lambda_lib.s3_request import S3Request

MAX_RETRIES = 1

logger = Logger()
xray_tracer = Tracer()


@xray_tracer.capture_lambda_handler
def handler(event, context):
    logger.info({"message": "lambda failure event received", "event": event})
    request_payload = event["requestPayload"]
    retry_count = request_payload.get("retryCount", 0)
    error_type = event["responsePayload"]["errorType"]
    if retry_count < MAX_RETRIES and error_type == "TimeoutError":
        logger.info({"message": f"retrying event after {retry_count} retries", "event": event})
        request_payload["retryCount"] = retry_count + 1
        async_invoke(event["requestContext"]["functionArn"], request_payload)
    else:
        for record in request_payload["Records"]:
            logger.info({"message": f"moving record after {retry_count} retries to error folder", "event": event})
            s3_key = record["s3"]["object"]["key"]
            error = f'{error_type}: {event["responsePayload"]["errorMessage"]}'
            S3Request(s3_key).update(actions=[S3Request.error.set(error)])
            move(record["s3"]["bucket"]["name"], s3_key, "error")
