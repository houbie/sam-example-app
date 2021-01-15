import io
import json
import os

import pytest

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
    def to_stream(obj):
        return io.BytesIO(json.dumps(obj).encode())

    return to_stream
