"""Three-pillar observability: structured logging, distributed tracing, metrics."""

import logging
import sys

import structlog
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import Counter

from src.config import settings

# ── Custom Prometheus counters ─────────────────────────────────────────────────

ocr_jobs_total = Counter(
    "ocr_jobs_total",
    "Total OCR jobs processed",
    ["status"],  # success | failed
)

# ── Logging ───────────────────────────────────────────────────────────────────


def _get_shared_processors() -> list:
    return [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]


def configure_logging() -> None:
    is_dev = settings.ENVIRONMENT == "development"

    renderer = (
        structlog.dev.ConsoleRenderer()
        if is_dev
        else structlog.processors.JSONRenderer()
    )

    structlog.configure(
        processors=[
            *_get_shared_processors(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG if is_dev else logging.INFO),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=_get_shared_processors(),
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG if is_dev else logging.INFO)

    # Silence noisy libraries
    for noisy in ("uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING if not is_dev else logging.INFO)


# ── Tracing ───────────────────────────────────────────────────────────────────


def configure_tracing(app=None, engine=None) -> None:
    resource = Resource(attributes={SERVICE_NAME: "rcbl-backend"})
    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(endpoint=settings.OTLP_ENDPOINT, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    if app is not None:
        FastAPIInstrumentor.instrument_app(app)

    if engine is not None:
        SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)


def get_tracer(name: str = "rcbl-backend") -> trace.Tracer:
    return trace.get_tracer(name)
