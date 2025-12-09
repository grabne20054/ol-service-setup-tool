from pydantic import BaseModel

class Status(BaseModel):
    job_id: str
    status: str

class StatusResponse(BaseModel):
    message: str
    status: int