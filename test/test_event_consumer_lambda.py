import json


def test_echo(flask_client):
    response = flask_client.get("/echo/part_1/part_2?q1=query-1&q2=query-2")
    assert response.status_code == 200
    body = json.loads(response.data)
    assert body == {
        "message": "echoing",
        "pathParam1": "part_1",
        "pathParam2": "part_2",
        "query-params": {
            "q1": "query-1",
            "q2": "query-2"}
    }
