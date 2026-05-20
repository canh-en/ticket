# trigger alarms realtime

import time
from telemetry_collector import collect_telemetry


CPU_THRESHOLD = 0.8


def detect_alarm(service_data):

    alarms = []

    service = service_data["service"]

    cpu_result = service_data["metrics"]["cpu"]

    try:
        result = cpu_result["data"]["result"]

        if len(result) > 0:

            values = result[0]["values"]

            latest = float(values[-1][1])

            if latest > CPU_THRESHOLD:

                alarms.append({
                    "service": service,
                    "metric": "cpu",
                    "value": latest
                })

    except Exception as e:
        print(e)

    return alarms


while True:

    telemetry = collect_telemetry(minutes=5)

    all_alarms = []

    for service_data in telemetry:

        alarms = detect_alarm(service_data)

        all_alarms.extend(alarms)

    if len(all_alarms) > 0:

        print("ALARM DETECTED")

        for alarm in all_alarms:
            print(alarm)

        # TODO:
        # call Nezha RCA here

    time.sleep(30)