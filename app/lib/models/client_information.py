from pydantic import BaseModel

class ClientInformation(BaseModel):
    company_name: str
    callback_url: str
