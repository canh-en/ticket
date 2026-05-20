# gom metrics + traces

from prometheus_client import get_service_metrics
from tempo_client import search_traces

SERVICES = [
    "ts-travel-service",
    "ts-order-service",
    "ts-seat-service"
]


def collect_telemetry(minutes=5):

    telemetry = []

    for service in SERVICES:

        metrics = get_service_metrics(service, minutes)

        traces = search_traces(service, minutes)

        telemetry.append({
            "service": service,
            "metrics": metrics,
            "traces": traces
        })

    return telemetry