import json
import os

def load_jobs():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    jobs_path = os.path.join(base_dir, "data", "jobs.json")

    with open(jobs_path, encoding="utf-8") as f:
        return json.load(f)