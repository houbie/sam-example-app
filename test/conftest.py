import io
import json
import os

import pytest
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))
sys.path.append(os.path.dirname(__file__))

from pytest_dynamodb import factories
from pytest_dynamodb.port import get_port

from lambda_lib.event_log import EventLog

EVENTS_PATH = "../events"
JSON_EXT = ".json"

os.environ["EVENT_CONSUMER_URL"] = "https://foo.bar"
os.environ["POWERTOOLS_TRACE_DISABLED"] = "1"


@pytest.fixture()
def load_event():
    def load(file: str) -> object:
        if not file.endswith(JSON_EXT):
            file += JSON_EXT
        event_file = os.path.join(os.path.dirname(__file__), EVENTS_PATH, file)
        return json.load(open(event_file, "r"))

    return load


@pytest.fixture()
def json_stream():
    def to_stream(obj: dict) -> io.BytesIO:
        return io.BytesIO(json.dumps(obj).encode())

    return to_stream


port = get_port(None)
dynamodb_proc = factories.dynamodb_proc(os.path.join(os.path.dirname(__file__), "../.dynamodb"), port=port)


@pytest.fixture()
def dynamo(dynamodb):
    EventLog.Meta.host = f"http://localhost:{port}"
    EventLog.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    return dynamodb
