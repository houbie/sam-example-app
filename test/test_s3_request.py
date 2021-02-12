from datetime import datetime, timezone

from lambda_lib.event_log import EventLog


def test_dynamodb(dynamo):
    """
    Simple test for DynamoDB.
    # Create a table
    # Put an item
    # Get the item and check the content of this item
    """
    req = EventLog("some-id", process_name="some-process", bucket="bucket_arn", s3_key="s3_key", received_time=datetime.now(timezone.utc))
    req.save()

    req2 = EventLog.get("some-id")
    req2.update(actions=[EventLog.processed_time.set(datetime.now(timezone.utc))])

    req.refresh()

    assert req.processed_time <= datetime.now(timezone.utc)
