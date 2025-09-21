# orchestrator/pipeline.py
import os, uuid, shutil
from pathlib import Path

from .providers.gemini import plan_spec, fix_invalid_json
from .codegen.validators import validate_spec
from .codegen.writer import write_files, zip_dir
from .agents.backend import generate_backend
from .agents.frontend import generate_frontend
from .storage.jobs import init_job, log, save_spec, complete, get_job_logs, get_job_result
from .mount_app import mount_generated_app

BUILDS_DIR = Path(os.getenv("BUILDS_DIR", "/tmp/builds"))

def start_build(payload: dict, root_app=None) -> str:   # <— accept root_app
    job_id = str(uuid.uuid4())
    workdir = BUILDS_DIR / job_id
    scaffold = Path(__file__).parent / "runtime" / "project_scaffold"

    shutil.copytree(scaffold, workdir)
    init_job(job_id, str(workdir))

    # 1) PLAN
    log(job_id, "manager:start")
    idea, domain = payload.get("idea"), payload.get("domain")
    spec_json = plan_spec(idea=idea, domain=domain)
    spec = validate_spec(spec_json) or validate_spec(fix_invalid_json(spec_json))
    if not spec:
        raise ValueError("Could not produce a valid spec.")
    save_spec(job_id, spec)

    # 2) BACKEND
    log(job_id, "backend:start")
    backend_files = generate_backend(spec, workdir)
    write_files(workdir, backend_files)

    # 3) FRONTEND
    log(job_id, "frontend:start")
    frontend_files = generate_frontend(spec, workdir)
    write_files(workdir, frontend_files)

    # 4) MOUNT (if app was provided)
    log(job_id, "mount:start")
    if root_app is not None:
        mount_generated_app(root_app, job_id, workdir)

    # 5) PACKAGE
    zip_path = zip_dir(workdir, f"{job_id}.zip")
    complete(job_id, {"zip_path": str(zip_path), "preview_url": f"/apps/{job_id}/"})
    log(job_id, "done")
    return job_id

def get_logs(job_id: str):
    return get_job_logs(job_id)

def get_result(job_id: str):
    return get_job_result(job_id)
