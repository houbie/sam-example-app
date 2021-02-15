import json

from sam_example_app.event_consumer_lambda import app


def test_echo():
    with app.test_client() as test_client:
        response = test_client.get("/echo/part_1/part_2?q1=query-1&q2=query-2")
        assert response.status_code == 200
        body = json.loads(response.data)
        assert body == {"message": "echoing",
                        "pathParam1": "part_1",
                        "pathParam2": "part_2",
                        "query-params": {"q1": "query-1", "q2": "query-2"}}
