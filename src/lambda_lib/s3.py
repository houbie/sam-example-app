import boto3

s3_client = boto3.client('s3')


def move(bucket: str, key: str, destination_folder: str):
    source_folder = key.partition("/")[0]
    destination_key = key.replace(source_folder, destination_folder)
    s3_client.copy_object(Bucket=bucket, Key=destination_key, CopySource=f"/{bucket}/{key}")
    s3_client.delete_object(Bucket=bucket, Key=key)
