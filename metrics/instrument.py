# instrument.py
from fastapi import FastAPI
from prometheus_client import start_http_server
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider

def instrument_app(app: FastAPI):
    """Configures OpenTelemetry instrumentation for the FastAPI app."""

    # Start a Prometheus client server to expose metrics.
    # This is the endpoint Prometheus will scrape.
    start_http_server(port=8001, addr="0.0.0.0")

    # Set up the OpenTelemetry Metrics provider.
    reader = PrometheusMetricReader()
    provider = MeterProvider(metric_readers=[reader])
    metrics.set_meter_provider(provider)

    # Instrument the FastAPI app.
    # This will automatically track requests, latency, errors, etc.
    FastAPIInstrumentor.instrument_app(app)

    print("✅ FastAPI application successfully instrumented with OpenTelemetry.")
    print("📈 Metrics available at: http://localhost:8001/metrics")