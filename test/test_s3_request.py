from datetime import datetime, timezone

from lambda_lib.s3_request import S3Request


def test_dynamodb(dynamo):
    """
    Simple test for DynamoDB.
    # Create a table
    # Put an item
    # Get the item and check the content of this item
    """
    req = S3Request("some-id", process_name="some-process",bucket="bucket_arn", s3_key="s3_key", received_time=datetime.now(timezone.utc))
    req.save()

    req2 = S3Request.get("some-id")
    req2.update(actions=[S3Request.processed_time.set(datetime.now(timezone.utc))])

    req.refresh()

    assert req.processed_time <= datetime.now(timezone.utc)
