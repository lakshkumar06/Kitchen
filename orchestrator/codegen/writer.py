from pathlib import Path
import zipfile, os

def write_files(root: Path, files: dict):
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

def zip_dir(root: Path, zip_name: str):
    z = root.parent / zip_name
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for folder, _, files in os.walk(root):
            for f in files:
                full = Path(folder)/f
                zf.write(full, arcname=full.relative_to(root))
    return z
