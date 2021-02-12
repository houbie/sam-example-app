from aws_lambda_powertools import Tracer, Logger

from lambda_lib.event_log import EventLog

MAX_RETRIES = 1

logger = Logger()
xray_tracer = Tracer()


@xray_tracer.capture_lambda_handler
def handler(event, *_):
    logger.info({"message": "lambda failure event received", "event": event})
    request_payload = event["requestPayload"]
    error_type = event["responsePayload"]["errorType"]
    # retry_count = request_payload.get("retryCount", 0)
    # if retry_count < MAX_RETRIES and error_type == "TimeoutError":
    #     logger.info({"message": f"retrying event after {retry_count} retries", "event": event})
    #     request_payload["retryCount"] = retry_count + 1
    #     async_invoke(event["requestContext"]["functionArn"], request_payload)
    # else:

    for record in request_payload["Records"]:
        s3_key = record["s3"]["object"]["key"]
        error = f'{error_type}: {event["responsePayload"]["errorMessage"]}'
        logger.error({"message": f"event failed", "error": error})
        EventLog(s3_key).update(actions=[EventLog.error.set(error)])
