import serverless_wsgi
from aws_lambda_powertools import Logger
from flask import Flask, jsonify, request

logger = Logger()

app = Flask(__name__)


def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)


@app.route("/consumer-events", methods=["POST"])
def consume_event():
    # trace.get_current_span().set_attribute("name", event.get("NAME", "no name provided"))
    logger.info({"message": "Consuming event", "event": request.json})
    return jsonify({"message": "consumed event"})


@app.route("/echo/<path_param_1>/<path_param_2>", methods=["GET"])
def handle_foo(path_param_1, path_param_2):
    logger.info({"event": request.environ['serverless.event'], "context": vars(request.environ['serverless.context'])})
    resp = {"message": "echoing",
            "pathParam1": path_param_1,
            "pathParam2": path_param_2,
            "query-params": request.args}
    return jsonify(resp)
