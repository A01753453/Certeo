import argparse
from app.db import SessionLocal
from app.models import Empresa

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--rfc", required=False, default=None)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        e = Empresa(nombre=args.name, rfc=args.rfc)
        db.add(e)
        db.commit()
        db.refresh(e)
        print("Empresa creada:")
        print("  id:", e.id)
        print("  nombre:", e.nombre)
        print("  rfc:", e.rfc)
    finally:
        db.close()

if __name__ == "__main__":
    main()
