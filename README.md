# Copiloto de Cumplimiento — MVP Día 1

Stack: FastAPI + SQLite (local). Día 1 incluye:
- Endpoint `POST /v1/ingesta/upload?empresa_id=<uuid>` (ZIP o XML)
- Endpoint `GET /v1/ingesta/jobs/{job_id}`
- Modelos: empresa, load_file, load_error
- Almacenamiento local de archivos y hash SHA-256 para idempotencia
- Tarea de procesamiento en background (stub) que marca DONE

## Requisitos
- Python 3.10+
- pip

## Setup rápido
```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate  # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/create_db.py            # crea tablas
python scripts/create_empresa.py --name "Empresa Demo" --rfc "XAXX010101000"
# copia el id impreso y úsalo en el upload
uvicorn app.main:app --reload
```

## Probar upload
```bash
# ejemplo con curl (reemplazar EMP_ID e archivo)
curl -X POST "http://127.0.0.1:8000/v1/ingesta/upload?empresa_id=EMP_ID"         -H "Content-Type: multipart/form-data"         -F "file=@tests/samples/sample.xml"
```

## Estructura
```
app/
  api/ingesta.py
  services/{jobs.py, storage.py}
  utils/hash.py
  db.py
  models.py
  schemas.py
  main.py
scripts/{create_db.py, create_empresa.py}
tests/samples/{sample.xml, sample.zip}
storage/   # se genera al subir archivos
```

## Notas
- Día 1 usa SQLite para simplicidad. Día 2 se puede migrar a Postgres/Alembic.
- `load_file.status`: PENDING | PROCESSING | DONE | ERROR
