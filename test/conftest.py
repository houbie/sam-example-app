import json
import os

import pytest
from pytest_dynamodb import factories
from pytest_dynamodb.port import get_port

from sam_example_app.lambda_lib.event_log import EventLog

EVENTS_PATH = "../events"
JSON_EXT = ".json"

# configure the lambda handlers
os.environ["EVENT_CONSUMER_URL"] = "https://foo.bar"
# disable x-ray tracing
os.environ["POWERTOOLS_TRACE_DISABLED"] = "1"

dynamo_dir = os.path.join(os.path.dirname(__file__), "../.dynamodb")
if not os.path.exists(f"{dynamo_dir}/DynamoDBLocal.jar"):
    raise FileNotFoundError(f"DynamoDBLocal.jar not found. Run 'bin/download-dynamo-local.sh' first")
# find a free port and start local dynamodb
port = get_port(None)
dynamodb_proc = factories.dynamodb_proc(dynamo_dir, port=port)


@pytest.fixture()
def dynamo(dynamodb):
    EventLog.Meta.host = f"http://localhost:{port}"
    EventLog.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    return dynamodb


@pytest.fixture()
def load_event():
    def load(file: str) -> object:
        if not file.endswith(JSON_EXT):
            file += JSON_EXT
        event_file = os.path.join(os.path.dirname(__file__), EVENTS_PATH, file)
        return json.load(open(event_file, "r"))

    return load
