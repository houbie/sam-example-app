import os

from pytest_mock import MockerFixture

from s3_event_lambda import handler


def test_handler(load_event, json_stream, mocker: MockerFixture):
    s3_event = load_event("s3_event")

    s3_get_object = mocker.patch("lambda_lib.s3.s3_client.get_object")
    s3_get_object.return_value = {"Body": json_stream({"data": "my event"})}
    mocker.patch("lambda_lib.s3.s3_client.copy_object")
    mocker.patch("lambda_lib.s3.s3_client.delete_object")

    http_post = mocker.patch("lambda_lib.power_requests.http.post")

    assert handler(s3_event, {}) == "Successfully processed event"
    http_post.assert_called_with(os.environ["EVENT_CONSUMER_URL"], json={"DATA": "my event"})
