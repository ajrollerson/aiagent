import json
from datetime import datetime

def log_event(event_type, **details):

    now = datetime.now()

    event = {
        "timestamp": now.strftime("%H:%M:%S.%f")[:-3],
        "type": event_type,
        **details,
    }

    with open("event_log.jsonl", "a") as f:
        f.write(json.dumps(event) + "\n")

def get_last_n_logs(n=5):

    with open("event_log.jsonl", "r") as f:
        logs = [json.loads(line) for line in f if line.strip()]

    return logs[-n:]

