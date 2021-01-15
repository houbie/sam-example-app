import json
import os

from pytest_mock import MockerFixture

import async_event_lambda
from async_event_api_lambda import handler
from lambda_lib.util import compress_base64


def test_handler(load_event, mocker: MockerFixture):
    """
    This will test the handler with all its decorators, so it requires a full proxy event and context as arguments.
    In a real project, the rest_api_handler decorator would be defined and tested in a library project. Testing the
    undecorated handler could then arguably be sufficient (see test_handler_unwrapped below).
    On the other hand, we can test here with a real proxy event that can be reused when invoking the lambda with sam.

    As proof of concept, the async_event_api_lambda and the async_event_lambda are chained together by the side_effect
    of the invoke_lambda mock, creating an end-to-end test
    """
    api_gw_event = load_event("api_gw_event")

    invoke_lambda = mocker.patch("lambda_lib.lmbda.lambda_client.invoke")
    # forward the payload of the lambda_client.invoke call to the async_event_lambda
    invoke_lambda.side_effect = lambda Payload, **kwargs: async_event_lambda.handler(Payload, {})

    http_post = mocker.patch("lambda_lib.power_requests.http.post")

    assert handler(api_gw_event, {}) == {'body': '{"message": "async invoked lambda ASYNC_HANDLER_FN_NOT_SET"}',
                                         'headers': {'Content-Type': 'application/json'}, 'statusCode': 200}

    invoke_lambda.assert_called_with(FunctionName="ASYNC_HANDLER_FN_NOT_SET", InvocationType="Event",
                                     Payload=f'"{compress_base64(api_gw_event["body"])}"')

    http_post.assert_called_with(os.environ["EVENT_CONSUMER_URL"], json={"MESSAGE": "hello world"})


def test_handler_unwrapped(mocker: MockerFixture):
    """
    This will test the undecorated async_event_api_lambda handler, making it an actual unit test.
    This results in a simpler tests that only tests the actual code in the module.
    """
    unwrapped_handler = handler.__wrapped__.__wrapped__
    event = {"foo": "bar"}

    invoke_lambda = mocker.patch("lambda_lib.lmbda.lambda_client.invoke")

    assert unwrapped_handler(event) == {"message": "async invoked lambda ASYNC_HANDLER_FN_NOT_SET"}

    invoke_lambda.assert_called_with(FunctionName="ASYNC_HANDLER_FN_NOT_SET", InvocationType="Event",
                                     Payload=f'"{compress_base64(json.dumps(event))}"')
