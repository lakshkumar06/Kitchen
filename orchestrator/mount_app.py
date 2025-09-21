from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles
from importlib import util
from pathlib import Path

def mount_generated_app(root_app, job_id: str, job_dir: Path):
    # 1) Serve frontend
    root_app.mount(
        f"/apps/{job_id}",
        StaticFiles(directory=job_dir / "frontend" / "public", html=True),
        name=f"app-{job_id}-static"
    )
    # 2) Mount backend routers under /apps/{job}/api/*
    routers_dir = job_dir / "backend" / "app" / "routers"
    for py in routers_dir.glob("*.py"):
        if py.name == "__init__.py":
            continue
        spec = util.spec_from_file_location(f"{job_id}.{py.stem}", py)
        mod = util.module_from_spec(spec)  # type: ignore
        spec.loader.exec_module(mod)       # type: ignore
        router = getattr(mod, "router", None)
        if router:
            sub = APIRouter()
            sub.include_router(router, prefix=f"/api/{py.stem}s")
            root_app.include_router(sub, prefix=f"/apps/{job_id}")
