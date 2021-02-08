import io
import os

from pytest_mock import MockerFixture

from lambda_lib.s3_request import S3Request
from s3_event_lambda import handler


def test_handler(load_event, dynamo, mocker: MockerFixture):
    s3_event = load_event("s3_event")

    get_object = mocker.patch("lambda_lib.s3.s3_client.get_object")
    get_object.return_value = {"Body": io.StringIO('{"name": "foobar"}'),
                               "Metadata": {"x-b3-traceid": "463ac35c9f6413ad48485a3953bb6124",
                                            "x-b3-spanid": "a2fb4a1d1a96d312", }}
    mocker.patch("lambda_lib.s3.move")

    http_post = mocker.patch("lambda_lib.power_requests.http.post")

    assert handler(s3_event, {}) == "Successfully processed event"
    http_post.assert_called_with(os.environ["EVENT_CONSUMER_URL"], json={"NAME": "foobar"})

    req = S3Request.scan(S3Request.functional_key == "foobar").next()
    assert req.trace_id == "463ac35c9f6413ad48485a3953bb6124"
    assert req.processed_time
