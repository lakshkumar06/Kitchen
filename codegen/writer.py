"""Safe file operations and project generation"""

import os
import shutil
import zipfile
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any


class ProjectWriter:
    """Handles project generation from templates"""

    def __init__(self, templates_dir: str = "codegen/templates"):
        self.templates_dir = Path(templates_dir)
        self.jinja_env = Environment(loader=FileSystemLoader(str(self.templates_dir)))

    def generate_project(self, project_data: Dict[str, Any], output_dir: str = "EXAMPLE_PROJECT") -> str:
        """Generate complete project from templates"""
        project_path = Path(output_dir)

        # Clean and create project directory
        if project_path.exists():
            shutil.rmtree(project_path)
        project_path.mkdir(parents=True)

        # Create directory structure
        self._create_directory_structure(project_path)

        # Generate backend files
        self._generate_backend_files(project_data, project_path)

        # Generate frontend files
        self._generate_frontend_files(project_data, project_path)

        # Generate configuration files
        self._generate_config_files(project_data, project_path)

        return str(project_path)

    def _create_directory_structure(self, project_path: Path):
        """Create project directory structure"""
        directories = [
            "app",
            "app/routers",
            "static/css",
            "static/js",
            "templates",
        ]

        for directory in directories:
            (project_path / directory).mkdir(parents=True, exist_ok=True)

    def _generate_backend_files(self, project_data: Dict[str, Any], project_path: Path):
        """Generate backend files from templates"""
        backend_templates = [
            ("db.py.j2", "app/db.py"),
            ("models.py.j2", "app/models.py"),
            ("schemas.py.j2", "app/schemas.py"),
            ("router.py.j2", "app/routers/api.py"),
            ("main.py.j2", "main.py"),
            ("seed.py.j2", "seed.py"),
        ]

        for template_name, output_path in backend_templates:
            self._render_template(template_name, project_data, project_path / output_path)

        # Create __init__.py files
        (project_path / "app/__init__.py").touch()
        (project_path / "app/routers/__init__.py").touch()

    def _generate_frontend_files(self, project_data: Dict[str, Any], project_path: Path):
        """Generate frontend files from templates"""
        frontend_templates = [
            ("index.html.j2", "templates/index.html"),
            ("styles.css.j2", "static/css/styles.css"),
            ("api.js.j2", "static/js/api.js"),
        ]

        for template_name, output_path in frontend_templates:
            self._render_template(template_name, project_data, project_path / output_path)

        # Generate entity-specific templates
        for entity in project_data.get("entities", []):
            entity_data = {**project_data, "entity": entity}

            # Generate list template
            list_output = project_path / f"templates/{entity['name'].lower()}_list.html"
            self._render_template("list.html.j2", entity_data, list_output)

            # Generate form template
            form_output = project_path / f"templates/{entity['name'].lower()}_form.html"
            self._render_template("form.html.j2", entity_data, form_output)

    def _generate_config_files(self, project_data: Dict[str, Any], project_path: Path):
        """Generate configuration files"""
        # Generate Dockerfile
        self._render_template("Dockerfile.backend.j2", project_data, project_path / "Dockerfile")

        # Generate requirements.txt
        requirements = [
            "fastapi>=0.68.0",
            "uvicorn[standard]>=0.15.0",
            "sqlalchemy>=1.4.0",
            "pydantic>=1.8.0",
            "python-multipart>=0.0.5",
        ]

        with open(project_path / "requirements.txt", "w") as f:
            f.write("\n".join(requirements))

        # Generate .gitignore
        gitignore_content = """
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Database
*.db
*.sqlite3

# Environment variables
.env
.venv
env/
venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        with open(project_path / ".gitignore", "w") as f:
            f.write(gitignore_content.strip())

    def _render_template(self, template_name: str, data: Dict[str, Any], output_path: Path):
        """Render a template to a file"""
        try:
            template = self.jinja_env.get_template(template_name)
            content = template.render(**data)

            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

        except Exception as e:
            raise Exception(f"Failed to render template {template_name}: {str(e)}")

    def create_zip_archive(self, project_path: str, zip_name: str = None) -> str:
        """Create a ZIP archive of the generated project"""
        if not zip_name:
            zip_name = f"{Path(project_path).name}.zip"

        zip_path = Path(zip_name)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(Path(project_path))
                    zipf.write(file_path, arcname)

        return str(zip_path)


# Global writer instance
project_writer = ProjectWriter()