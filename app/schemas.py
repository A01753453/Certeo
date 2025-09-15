from pydantic import BaseModel

class JobOut(BaseModel):
    job_id: str
    status: str
    empresa_id: int
    sha256: str
    records_count: int
    invoices_count: int

    class Config:
        from_attributes = True
