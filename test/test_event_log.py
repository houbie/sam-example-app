from datetime import datetime, timezone

from sam_example_app.lambda_lib.event_log import EventLog


def test_dynamodb(dynamo):
    """
    Simple test for DynamoDB.
    # Create a table
    # Put an item
    # Get the item and check the content of this item
    """
    event_log = EventLog("some-id", process_name="some-process", bucket="bucket_arn", s3_key="s3_key",
                         received_time=datetime.now(timezone.utc))
    event_log.save()

    event_log2 = EventLog.get("some-id")
    event_log2.update(actions=[EventLog.processed_time.set(datetime.now(timezone.utc))])

    event_log.refresh()

    assert event_log.processed_time <= datetime.now(timezone.utc)
