import os
from pathlib import Path

STORAGE_DIR = os.getenv("STORAGE_DIR", "./storage")

def ensure_storage_dir(empresa_id: str) -> Path:
    path = Path(STORAGE_DIR) / empresa_id
    path.mkdir(parents=True, exist_ok=True)
    return path

def save_raw_file(empresa_id: str, sha256: str, filename: str, data: bytes) -> str:
    folder = ensure_storage_dir(empresa_id)
    ext = ".zip" if filename.lower().endswith(".zip") else ".xml"
    out = folder / f"{sha256}{ext}"
    with open(out, "wb") as f:
        f.write(data)
    return str(out)
