# query traces

import requests
import time

TEMPO_URL = "http://tempo:3200"


def search_traces(service, minutes=5):

    end_ns = int(time.time() * 1e9)
    start_ns = end_ns - minutes * 60 * 1_000_000_000

    url = f"{TEMPO_URL}/api/search"

    params = {
        "start": start_ns,
        "end": end_ns,
        "tags": f"service.name={service}",
        "limit": 20
    }

    resp = requests.get(url, params=params)

    return resp.json()


def get_trace(trace_id):

    url = f"{TEMPO_URL}/api/traces/{trace_id}"

    resp = requests.get(url)

    return resp.json()