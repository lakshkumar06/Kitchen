import time
_jobs = {}

def init_job(job_id: str, workdir: str):
    _jobs[job_id] = {"workdir": workdir, "events": [], "result": None}

def log(job_id: str, message: str):
    _jobs[job_id]["events"].append({"t": time.time(), "msg": message})

def save_spec(job_id: str, spec: dict):
    _jobs[job_id]["spec"] = spec

def complete(job_id: str, result: dict):
    _jobs[job_id]["result"] = result

def get_job_logs(job_id: str):
    return _jobs.get(job_id, {}).get("events", [])

def get_job_result(job_id: str):
    return _jobs.get(job_id, {}).get("result")
