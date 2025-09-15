import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, BigInteger, CheckConstraint, CHAR
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import LargeBinary
from sqlalchemy.sql import func
from sqlalchemy import Integer

from .db import Base

def gen_uuid():
    return str(uuid.uuid4())

class Empresa(Base):
    __tablename__ = "empresa"
    id = Column(String, primary_key=True, default=gen_uuid)
    nombre = Column(Text, nullable=False)
    rfc = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    load_files = relationship("LoadFile", back_populates="empresa")

class LoadFile(Base):
    __tablename__ = "load_file"
    id = Column(String, primary_key=True, default=gen_uuid)
    empresa_id = Column(String, ForeignKey("empresa.id"), nullable=False)
    filename = Column(Text, nullable=False)
    sha256 = Column(CHAR(64), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(Text, nullable=False)  # PENDING/PROCESSING/DONE/ERROR

    empresa = relationship("Empresa", back_populates="load_files")
    errors = relationship("LoadError", back_populates="load_file")

class LoadError(Base):
    __tablename__ = "load_error"
    id = Column(String, primary_key=True, default=gen_uuid)
    load_file_id = Column(String, ForeignKey("load_file.id"), nullable=False)
    xml_name = Column(Text, nullable=True)
    code = Column(Text, nullable=True)
    message = Column(Text, nullable=True)
    context = Column(Text, nullable=True)  # JSON as text for SQLite simplicity
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    load_file = relationship("LoadFile", back_populates="errors")
