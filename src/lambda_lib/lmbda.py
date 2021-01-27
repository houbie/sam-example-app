import json
from typing import Union

import boto3

from lambda_lib.util import compress_base64

lambda_client = boto3.client('lambda')


def async_invoke(lambda_identifier: str, payload: Union[str, dict], compress: bool = False) -> dict:
    if type(payload) != str:
        payload = json.dumps(payload)
    if compress:
        payload = compress_base64(payload)
    return lambda_client.invoke(
        FunctionName=lambda_identifier,
        InvocationType='Event',
        Payload=payload
    )
