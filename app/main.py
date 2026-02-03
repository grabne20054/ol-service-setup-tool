from fastapi import FastAPI, BackgroundTasks
from lib.models import client_information
from lib.init_service.setup_service import SetupService
from lib.models.status import  StatusResponse
from lib.init_service.setup_initated import SetupInitiated
from uuid import uuid4

app = FastAPI(openapi_webhooks={})

@app.post("/setup-service/", response_model=StatusResponse, status_code=202)
async def setup_service(company_info: client_information.ClientInformation, background_tasks: BackgroundTasks):
    
    def background_setup():
        setup_service = SetupService(
            service_name=company_info.company_name,
            initial_state=SetupInitiated(),
            callback_url=company_info.callback_url
        )
        setup_service.run()
    background_tasks.add_task(background_setup)
    job_id = str(uuid4())
    return StatusResponse(message=f"Service setup job {job_id} initiated for {company_info.company_name}", status=202)




