import json

import boto3

from lambda_lib.util import compress_base64

lambda_client = boto3.client('lambda')


def async_invoke(lambda_name: str, payload: str, compress: bool = True) -> dict:
    if compress:
        payload = compress_base64(payload)
    return lambda_client.invoke(
        FunctionName=lambda_name,
        InvocationType='Event',
        Payload=json.dumps(payload)
    )
