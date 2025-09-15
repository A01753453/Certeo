from fastapi import APIRouter, UploadFile, HTTPException, BackgroundTasks
from fastapi import Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import json

from ..db import SessionLocal
from ..models import Empresa, LoadFile, LoadError
from ..schemas import UploadResponse, JobStatus
from ..utils.hash import sha256_bytes
from ..services.storage import save_raw_file
from ..services.jobs import process_load_file

router = APIRouter(prefix="/v1/ingesta", tags=["ingesta"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    empresa_id: str = Query(..., description="UUID de la empresa"),
    file: UploadFile = None,
    db: Session = Depends(get_db)
):
    if file is None:
        raise HTTPException(status_code=400, detail="Se requiere archivo .zip o .xml")

    empresa = db.get(Empresa, empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    data = await file.read()
    sha = sha256_bytes(data)

    # Idempotencia: si ya existe, regresamos el job_id existente
    lf = (
        db.query(LoadFile)
        .filter(LoadFile.empresa_id == empresa_id, LoadFile.sha256 == sha)
        .first()
    )
    if lf:
        return UploadResponse(job_id=lf.id, status=lf.status)

    # Crear LoadFile y guardar archivo
    lf = LoadFile(
        empresa_id=empresa_id,
        filename=file.filename,
        sha256=sha,
        size_bytes=len(data),
        status="PENDING",
    )
    db.add(lf)
    db.commit()
    db.refresh(lf)

    save_raw_file(empresa_id, sha, file.filename, data)

    # Encolar (background)
    background_tasks.add_task(process_load_file, db, lf.id)

    return UploadResponse(job_id=lf.id, status=lf.status)

@router.get("/jobs/{job_id}", response_model=JobStatus)
def job_status(job_id: str, db: Session = Depends(get_db)):
    lf = db.get(LoadFile, job_id)
    if not lf:
        raise HTTPException(status_code=404, detail="Job no encontrado")

    # Día 1: métricas dummy
    processed = 0
    inserted = 0
    errors = db.query(LoadError).filter(LoadError.load_file_id == job_id).count()

    return JobStatus(
        job_id=job_id,
        status=lf.status,
        processed_xmls=processed,
        inserted_xmls=inserted,
        error_xmls=errors,
    )
