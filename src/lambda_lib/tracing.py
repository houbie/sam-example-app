import typing
from contextlib import contextmanager

from aws_lambda_powertools import Logger
from opentelemetry import (propagators, trace, )
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.propagators.b3 import B3Format
from opentelemetry.sdk.trace import TracerProvider, Span
from opentelemetry.sdk.trace.export import (SimpleExportSpanProcessor, SpanExporter, SpanExportResult, )
from opentelemetry.trace import SpanKind
from opentelemetry.trace.propagation.textmap import DictGetter
from requests.adapters import HTTPAdapter, CaseInsensitiveDict

from lambda_lib.power_requests import http

logger = Logger()


def format_trace_id(trace_id: int) -> str:
    return "{:032x}".format(trace_id)


def format_span_id(span_id: int) -> str:
    return "{:016x}".format(span_id)


class LoggerSpanExporter(SpanExporter):
    """Implementation of :class:`SpanExporter` that logs spans as json.
    """

    def __init__(
            self,
            service_name: typing.Optional[str] = None,
    ):
        self.service_name = service_name

    def export(self, spans: typing.Sequence[Span]) -> SpanExportResult:
        for span in spans:
            ctx = span.get_span_context()
            msg = {
                "type": "_DIST_TRACING_DATA_",
                "payload": {
                    "name": span.name,
                    "kind": span.kind,
                    "parentSpanId": format_span_id(span.parent.span_id),
                    "context": {
                        "spanId": format_span_id(ctx.span_id),
                        "traceId": format_trace_id(ctx.trace_id),
                        "sampled": ctx.trace_flags.sampled
                    },
                    "startTimestamp": span.start_time,
                    "endTimestamp": span.end_time,
                    "attributes": span.attributes,
                    "status": {
                        "code": span.status.status_code,
                        "description": span.status.description
                    }
                }
            }
            logger.info(msg)
        return SpanExportResult.SUCCESS


RequestsInstrumentor().instrument()
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(LoggerSpanExporter())
)
tracer = trace.get_tracer(__name__)
propagators.set_global_textmap(B3Format())


@contextmanager
def start_root_span(name: str, trace_carrier: dict, kind: SpanKind = SpanKind.SERVER,
                    **kwargs) -> typing.Iterator["Span"]:
    lower_case_carrier = {key.lower(): value for key, value in trace_carrier.items()}
    lower_case_carrier["x-b3-sampled"] = "1"  # force sampling
    ctx = propagators.extract(DictGetter(), lower_case_carrier)
    with tracer.start_as_current_span(name, context=ctx, kind=kind, **kwargs) as span:
        yield span


class TracePropagatorHTTPAdapter(HTTPAdapter):
    """HTTPAdapter that injects trace headers
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        propagators.inject(CaseInsensitiveDict.__setitem__, request.headers)
        return super().send(request, **kwargs)


adapter = TracePropagatorHTTPAdapter()
http.mount("https://", adapter)
http.mount("http://", adapter)
