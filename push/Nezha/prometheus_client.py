# query realtime metrics

import requests
import time

PROM_URL = "http://prometheus:9090"


def query_range(promql, start_ts, end_ts, step="30s"):
    url = f"{PROM_URL}/api/v1/query_range"

    params = {
        "query": promql,
        "start": start_ts,
        "end": end_ts,
        "step": step
    }

    resp = requests.get(url, params=params)
    return resp.json()


def get_service_metrics(service, minutes=5):

    end_ts = int(time.time())
    start_ts = end_ts - minutes * 60

    cpu_query = f'''
    rate(container_cpu_usage_seconds_total{{container="{service}"}}[5m])
    '''

    memory_query = f'''
    container_memory_usage_bytes{{container="{service}"}}
    '''

    cpu_data = query_range(cpu_query, start_ts, end_ts)
    memory_data = query_range(memory_query, start_ts, end_ts)

    return {
        "cpu": cpu_data,
        "memory": memory_data
    }