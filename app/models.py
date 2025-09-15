import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Empresa(Base):
    __tablename__ = "empresas"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    rfc = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    jobs = relationship("Job", back_populates="empresa", cascade="all, delete-orphan")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    sha256 = Column(String, nullable=False, index=True)
    filename = Column(String, nullable=False)
    mime_type = Column(String, nullable=True)
    status = Column(String, default="PENDING", nullable=False)  # PENDING | PROCESSING | DONE | ERROR
    records_count = Column(Integer, default=0, nullable=False)
    invoices_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    empresa = relationship("Empresa", back_populates="jobs")

    __table_args__ = (
        UniqueConstraint("empresa_id", "sha256", name="uq_jobs_empresa_sha"),
    )
