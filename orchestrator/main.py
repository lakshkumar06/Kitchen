from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .pipeline import start_build, get_logs, get_result

app = FastAPI(title="AI App Builder")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

@app.post("/build/start")
def build_start(payload: dict):
    """
    payload: { "idea": "Build a task tracker" }
             or { "domain": "Healthcare" } (UI picks an idea separately)
    """
    job_id = start_build(payload, app)
    return {"job_id": job_id, "preview_url": f"/apps/{job_id}/"}

@app.get("/build/{job_id}/logs")
def build_logs(job_id: str):
    return {"events": get_logs(job_id)}

@app.get("/build/{job_id}/result")
def build_result(job_id: str):
    res = get_result(job_id)
    if not res:
        raise HTTPException(404, "No result yet")
    return res
