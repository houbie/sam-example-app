from datetime import datetime, timezone

from lambda_lib.s3_request import S3Request


def test_crud(dynamo):
    """
    Simple test for DynamoDB.
    # Create a table
    # Put an item
    # Get the item and check the content of this item
    """
    req = S3Request("some-id", process_name="some_process", bucket="bucket_arn", s3_key="s3_key",
                    received_time=datetime.now(timezone.utc))
    req.save()

    req2 = S3Request.get("some-id")
    req2.update(actions=[S3Request.processed_time.set(datetime.now(timezone.utc))])

    req.refresh()

    assert req.processed_time <= datetime.now(timezone.utc)


def test_unmarshal():
    dynamo_event = {
        "Records": [
            {
                "eventID": "should auto-approve",
                "eventName": "MODIFY",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "eu-west-1",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1605884451,
                    "Keys": {
                        "id": {
                            "S": "some-id"
                        }
                    },
                    "NewImage": {
                        "bucket": {
                            "S": "bucket_arn"
                        },
                        "s3_key": {
                            "S": "s3_key"
                        },
                        "proc": {
                            "S": "some_process"
                        },
                        "received": {
                            "S": "2021-02-09T15:16:13.054250+0000"
                        },
                        "id": {
                            "S": "some-id"
                        }
                    },
                    "ConsumedCapacity": {
                        "TableName": "s3-requests",
                        "CapacityUnits": 0.5
                    }
                }
            }
        ]
    }

    req = S3Request.from_raw_data(dynamo_event["Records"][0]["dynamodb"]["NewImage"])
    assert req.id == "some-id"
    assert req.bucket == "bucket_arn"
