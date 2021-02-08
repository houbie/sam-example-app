from opentelemetry import propagators
from opentelemetry.trace import SpanKind
from opentelemetry.trace.propagation.textmap import DictGetter
from requests import Response

from lambda_lib.power_requests import http
from lambda_lib.tracing import tracer


def test_propagation(mocker):
    http_send = mocker.patch("requests.adapters.HTTPAdapter.send")
    http_response = Response()
    http_response.status_code = 200
    http_send.return_value = http_response

    b3 = {"x-b3-traceid": "463ac35c9f6413ad48485a3953bb6124",
          "x-b3-spanid": "a2fb4a1d1a96d312",
          "x-b3-sampled": "1"}

    ctx = propagators.extract(DictGetter(), b3)
    with tracer.start_as_current_span("my-span", context=ctx) as parent:
        assert parent.context.trace_id == int(b3["x-b3-traceid"], 16)
        with tracer.start_as_current_span("child-span", kind=SpanKind.CLIENT) as child:
            child.set_attribute("foo", "bar")
            headers = {'X-Custom': 'Test'}
            http.get('https://acme.com', headers=headers)

    assert http_send.call_args.args[0].headers["x-b3-traceid"] == b3["x-b3-traceid"]
