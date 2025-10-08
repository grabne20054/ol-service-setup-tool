from fastapi import FastAPI
from lib.models import CompanyInformation
app = FastAPI()

@app.post("/setup-service/")
async def setup_service(company_info: CompanyInformation):

    return {"message": "Service setup complete", "company_info": company_info}