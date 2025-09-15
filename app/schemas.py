from pydantic import BaseModel
from typing import Optional

class UploadResponse(BaseModel):
    job_id: str
    status: str

class JobStatus(BaseModel):
    job_id: str
    status: str
    processed_xmls: int
    inserted_xmls: int
    error_xmls: int
