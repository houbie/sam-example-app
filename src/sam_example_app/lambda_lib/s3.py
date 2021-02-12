import json

import boto3

s3_client = boto3.client('s3')
s3_resource = boto3.resource("s3")


def move(bucket: str, key: str, destination_folder: str):
    source_folder = key.rsplit("/", maxsplit=1)[0]
    destination_key = key.replace(source_folder, destination_folder)
    s3_resource.Object(bucket, destination_key).copy_from(CopySource={"Bucket": bucket, "Key": key})
    s3_resource.Object(bucket, key).delete()


def get_json(bucket: str, key: str) -> object:
    s3_obj = s3_client.get_object(Bucket=bucket, Key=key)
    return json.load(s3_obj['Body']), s3_obj["Metadata"]
