from app.db import Base, engine
from app import models

def main():
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas.")

if __name__ == "__main__":
    main()
