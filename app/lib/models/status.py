from pydantic import BaseModel

class Status(BaseModel):
    id: str
    status: str