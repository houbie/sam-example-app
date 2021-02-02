import os

from pytest_mock import MockerFixture

from lambda_lib.s3_request import S3Request
from s3_event_lambda import handler


def test_handler(load_event, dynamo, mocker: MockerFixture):
    s3_event = load_event("s3_event")

    s3_get_json = mocker.patch("lambda_lib.s3.get_json")
    s3_get_json.return_value = {"name": "foobar"}, {"traceparent": "my-trace"}
    mocker.patch("lambda_lib.s3.move")

    http_post = mocker.patch("lambda_lib.power_requests.http.post")

    assert handler(s3_event, {}) == "Successfully processed event"
    http_post.assert_called_with(os.environ["EVENT_CONSUMER_URL"], json={"NAME": "foobar"})

    req = S3Request.scan(S3Request.functional_key == "foobar").next()
    assert req.trace_parent == "my-trace"
    assert req.processed_time
