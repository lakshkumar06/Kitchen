from jinja2 import Environment, FileSystemLoader
from pathlib import Path

TPL_DIR = Path(__file__).resolve().parents[1] / "codegen" / "templates"
env = Environment(loader=FileSystemLoader(str(TPL_DIR)), trim_blocks=True, lstrip_blocks=True)

def generate_backend(spec: dict, workdir: Path) -> dict:
    files = {}
    files["backend/app/db.py"]      = env.get_template("db.py.j2").render()
    files["backend/app/models.py"]  = env.get_template("models.py.j2").render(spec=spec)
    files["backend/app/schemas.py"] = env.get_template("schemas.py.j2").render(spec=spec)
    # one router per entity
    for ent in spec["entities"]:
        files[f"backend/app/routers/{ent['name'].lower()}.py"] = env.get_template("router.py.j2").render(entity=ent)
    files["backend/app/main.py"]    = env.get_template("main.py.j2").render(entities=spec["entities"])
    files["backend/seed.py"]        = env.get_template("seed.py.j2").render(entities=spec["entities"])
    files["backend/requirements.txt"] = "fastapi\nuvicorn\nsqlalchemy\npydantic\npython-dotenv\n"
    files["backend/Dockerfile"]       = env.get_template("Dockerfile.backend.j2").render()
    return files
