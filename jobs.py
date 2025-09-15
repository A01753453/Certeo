from datetime import datetime
from sqlalchemy.orm import Session
from ..models import LoadFile

# Día 1: stub. Solo marca PROCESSING -> DONE. (El parseo llegará en Día 3.)
def process_load_file(db: Session, load_file_id: str) -> None:
    lf = db.get(LoadFile, load_file_id)
    if not lf:
        return
    lf.status = "PROCESSING"
    db.commit()
    db.refresh(lf)

    # Aquí se haría: descomprimir ZIP, iterar XMLs, insertar, registrar errores, etc.
    # Por ahora solo cambiamos a DONE.
    lf.status = "DONE"
    lf.processed_at = datetime.utcnow()
    db.commit()
