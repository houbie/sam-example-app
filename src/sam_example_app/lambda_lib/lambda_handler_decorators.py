import json
from datetime import datetime, timezone
from functools import wraps
from json import JSONDecodeError
from typing import Callable, Tuple

import dateutil.parser
from aws_lambda_powertools import Logger
from jsonpath_ng import parse

import sam_example_app.lambda_lib.s3 as s3
from sam_example_app.lambda_lib.event_log import EventLog
from sam_example_app.lambda_lib.tracing import start_root_span
from sam_example_app.lambda_lib.util import decompress_base64

logger = Logger()


def s3_json_event_handler(process_name: str, functional_key: Tuple[str, str]) -> Callable:
    def decorator(func: Callable[[object, dict], None]):
        functional_key_name, functional_key_path = functional_key
        jsonpath_expr = parse(functional_key_path)

        @wraps(func)
        def wrapper(event, _context):
            logger.info({"message": "s3_json_event_handler", "records": len(event['Records'])})
            for record in event['Records']:
                bucket = record['s3']['bucket']['name']
                key = record['s3']['object']['key']
                s3_obj = s3.s3_client.get_object(Bucket=bucket, Key=key)
                meta_data = s3_obj["Metadata"]
                with start_root_span(f"{func.__module__}.{func.__name__}", meta_data) as span:
                    try:
                        body = json.load(s3_obj['Body'])
                        event_log = audit(body, bucket, key, span,
                                          record["requestParameters"]["sourceIPAddress"],
                                          dateutil.parser.parse(record["eventTime"]))

                        # invoke wrapped function
                        result = func(body, meta_data)

                        event_log.update(actions=[EventLog.processed_time.set(datetime.now(timezone.utc))])
                        return result
                    except JSONDecodeError:
                        message = f"S3 object {key} in bucket {bucket} is not valid Json"
                        logger.exception(message)
                        event_log.update(actions=[EventLog.error.set(message)])
                    except Exception as e:
                        logger.exception(f'Error getting object {key} from bucket {bucket}:')
                        raise e  # exception will trigger lambda retry

        def audit(body, bucket, key, span, source_ip_address, received_time):
            matches = jsonpath_expr.find(body)
            functional_key_value = matches[0].value if matches else f"{functional_key_path} not found"
            logger.structure_logs(append=True, **{functional_key_name: functional_key_value})
            span.set_attribute(functional_key_name, functional_key_value)
            logger.info({"message": "s3_json_event_handler", "bucket": bucket, "key": key})
            event_log = EventLog(id=key,
                                 process_name=process_name,
                                 functional_key=functional_key_value,
                                 bucket=bucket,
                                 s3_key=key,
                                 source_ip_address=source_ip_address,
                                 trace_id="{:032x}".format(span.get_span_context().trace_id),
                                 received_time=received_time)
            event_log.save()
            return event_log

        return wrapper

    return decorator


def rest_api_handler(func: Callable[[dict], object]):
    @wraps(func)
    def wrapper(event, _context):
        logger.debug({"message": "json_post_event_handler", "event": event})
        with start_root_span(f"{func.__module__}.{func.__name__}", event["headers"]):
            try:
                body = json.loads(event['body'])
                result = func(body)
                return {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body": json.dumps(result)
                }
            except JSONDecodeError:
                return {
                    "statusCode": 400,
                    "body": "Invalid Json"
                }

    return wrapper


def compressed_json_event_handler(func: Callable[[object], object]):
    @wraps(func)
    def wrapper(event, _context):
        logger.debug({"message": "compressed_event_handler", "event": event})
        decompressed = decompress_base64(event)
        return func(json.loads(decompressed))

    return wrapper
