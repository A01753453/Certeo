import os
import shutil
import time
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.config import settings
from app.database import get_db, Base, engine
from app.models import Empresa, Job
from app.schemas import JobOut
from app.utils import sha256_stream

app = FastAPI(title="Ingesta & Esquema - Día 1")

# Ensure storage dir exists
os.makedirs(settings.STORAGE_DIR, exist_ok=True)

@app.get("/health")
def health():
    return {"ok": True, "ts": datetime.utcnow().isoformat()}

def _ensure_empresa(db: Session, empresa_id: int) -> Empresa:
    empresa = db.scalar(select(Empresa).where(Empresa.id == empresa_id))
    if not empresa:
        raise HTTPException(status_code=404, detail="empresa_id not found")
    return empresa

def _ext_from_filename(name: str) -> str:
    lname = name.lower()
    if lname.endswith(".zip"):
        return ".zip"
    if lname.endswith(".xml"):
        return ".xml"
    return ""

def _persist_stream_to_temp(upload: UploadFile, tmp_path: str) -> str:
    # Save to temp and compute sha256
    upload.file.seek(0)
    import hashlib
    hasher = hashlib.sha256()
    with open(tmp_path, "wb") as out:
        while True:
            chunk = upload.file.read(1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
            out.write(chunk)
    upload.file.seek(0)
    return hasher.hexdigest()

def _process_job(job_id: str):
    # NOTE: executed after response via BackgroundTasks
    from app.database import SessionLocal
    with SessionLocal() as db:
        job = db.get(Job, job_id)
        if not job:
            return
        # PROCESSING
        job.status = "PROCESSING"
        job.updated_at = datetime.utcnow()
        db.commit()

        # Simulate work
        time.sleep(2)

        # Set dummy counters and DONE
        job.records_count = 42
        job.invoices_count = 7
        job.status = "DONE"
        job.updated_at = datetime.utcnow()
        db.commit()

@app.post("/v1/ingesta/upload", response_model=JobOut)
async def upload_file(
    background: BackgroundTasks,
    empresa_id: int = Query(..., description="ID de la empresa dueña del archivo"),
    file: UploadFile = File(..., description="Archivo ZIP o XML"),
    db: Session = Depends(get_db),
):
    # Validaciones mínimas
    if file is None:
        raise HTTPException(status_code=400, detail="file is required")
    _ensure_empresa(db, empresa_id)

    # Checar extensión permitida
    ext = _ext_from_filename(file.filename or "")
    if ext not in (".zip", ".xml"):
        raise HTTPException(status_code=400, detail="file must be .zip or .xml")

    # Persistimos temporalmente para calcular sha256 sin cargar todo en memoria
    empresa_dir = os.path.join(settings.STORAGE_DIR, str(empresa_id))
    os.makedirs(empresa_dir, exist_ok=True)
    tmp_path = os.path.join(empresa_dir, f"tmp_{int(time.time()*1000)}")
    sha = _persist_stream_to_temp(file, tmp_path)

    # Idempotencia por (empresa_id, sha256)
    existing = db.execute(
        select(Job).where(Job.empresa_id == empresa_id, Job.sha256 == sha)
    ).scalar_one_or_none()
    if existing:
        # Borrar temporales y regresar el mismo job_id
        try:
            os.remove(tmp_path)
        except FileNotFoundError:
            pass
        return JobOut(
            job_id=existing.id,
            status=existing.status,
            empresa_id=existing.empresa_id,
            sha256=existing.sha256,
            records_count=existing.records_count,
            invoices_count=existing.invoices_count,
        )

    # Mover archivo a nombre definitivo <sha256>.<ext>
    final_path = os.path.join(empresa_dir, f"{sha}{ext}")
    shutil.move(tmp_path, final_path)

    # Crear Job en estado PENDING
    job = Job(
        empresa_id=empresa_id,
        sha256=sha,
        filename=os.path.basename(final_path),
        mime_type=file.content_type,
        status="PENDING",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Disparar proceso en background
    background.add_task(_process_job, job.id)

    return JobOut(
        job_id=job.id,
        status=job.status,
        empresa_id=job.empresa_id,
        sha256=job.sha256,
        records_count=job.records_count,
        invoices_count=job.invoices_count,
    )

@app.get("/v1/ingesta/jobs/{job_id}", response_model=JobOut)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return JobOut(
        job_id=job.id,
        status=job.status,
        empresa_id=job.empresa_id,
        sha256=job.sha256,
        records_count=job.records_count,
        invoices_count=job.invoices_count,
    )
