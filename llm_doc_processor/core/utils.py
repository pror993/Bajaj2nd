import os
import json
import uuid
import numpy as np

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def default_json_serializer(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return str(obj)

def save_query_result(query_data):
    query_id = str(uuid.uuid4())
    path = os.path.join(RESULTS_DIR, f"{query_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(query_data, f, indent=2, default=default_json_serializer)
    return query_id

def load_query_result(query_id):
    path = os.path.join(RESULTS_DIR, f"{query_id}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
