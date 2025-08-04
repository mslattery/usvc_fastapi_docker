# metrics.py

from opentelemetry import metrics

# It's a good practice to use a name that identifies your application
# This will be the prefix for your metric names in some backends.
meter = metrics.get_meter(__name__)

app_counter = meter.create_counter(
    name="app.counter",
    description="Counts something",
    unit="1"
)