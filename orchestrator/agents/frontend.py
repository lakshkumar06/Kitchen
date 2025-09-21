from jinja2 import Environment, FileSystemLoader
from pathlib import Path  

TPL_DIR = Path(__file__).resolve().parents[1] / "codegen" / "templates"
env = Environment(loader=FileSystemLoader(str(TPL_DIR)), trim_blocks=True, lstrip_blocks=True)

def generate_frontend(spec: dict, workdir):
    files = {}
    files["frontend/public/index.html"]   = env.get_template("index.html.j2").render(spec=spec)
    files["frontend/public/js/api.js"]    = env.get_template("api.js.j2").render()
    files["frontend/public/css/styles.css"]= env.get_template("styles.css.j2").render()
    for page in spec["pages"]:
        if page["type"] == "list":
            files[f"frontend/public{page['path']}/index.html"] = env.get_template("list.html.j2").render(page=page, spec=spec)
        elif page["type"] == "form":
            files[f"frontend/public{page['path']}"] = env.get_template("form.html.j2").render(page=page, spec=spec)
    return files
