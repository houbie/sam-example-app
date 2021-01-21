import json
import urllib.parse
from functools import wraps
from json import JSONDecodeError
from typing import Callable

from aws_lambda_powertools import Logger

from lambda_lib.s3 import s3_client
from lambda_lib.util import decompress_base64

logger = Logger()


def s3_json_event_handler(func: Callable[[object], None]):
    @wraps(func)
    def wrapper(event, _context):
        logger.debug({"message": "s3_json_event_handler", "event": event})
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = urllib.parse.unquote_plus(record['s3']['object']['key'], encoding='utf-8')
            logger.info({"message": "s3_json_event_handler", "bucket": bucket, "key": key})
            try:
                s3_obj = s3_client.get_object(Bucket=bucket, Key=key)
                s3_json = json.load(s3_obj['Body'])
                result = func(s3_json)
                s3_client.copy_object(Bucket=bucket, Key=key.replace("in/", "out/"), CopySource=f"/{bucket}/{key}")
                s3_client.delete_object(Bucket=bucket, Key=key)
                return result
            except JSONDecodeError:
                logger.exception(f"S3 object {key} in bucket {bucket} is not valid Json")
            except Exception as e:
                logger.exception(f'Error getting object {key} from bucket {bucket}:')
                raise e

    return wrapper


def rest_api_handler(func: Callable[[dict], object]):
    @wraps(func)
    def wrapper(event, _context):
        logger.debug({"message": "json_post_event_handler", "event": event})
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
