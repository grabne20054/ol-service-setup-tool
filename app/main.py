from fastapi import FastAPI
from lib.models import company_information
from lib.coding_information import CodingInformationHandler
from lib.setup_service import SetupService
from lib.config_loader import ConfigLoader
from lib.update_rp_configs import UpdateRPConfigs
from lib.service_status import ServiceStatus
from lib.models.status import Status

from threading import Thread
app = FastAPI()

@app.post("/setup-service/")
async def setup_service(company_info: company_information.CompanyInformation):
    try:
        setup_service_instance = SetupService(service_name=company_info.company_name)
        thread = Thread(target=setup_service_instance.initialize_service)
        thread.start()
    except Exception as e:
        return {"error": str(e)}
    return {"message": f"Service setup initiated for {company_info.company_name}"}

@app.get("/service-status/{service_name}")
async def service_status(service_name: str):
    service_status_instance = ServiceStatus(service_name=service_name)
    status = service_status_instance.get_status()
    return Status(id=service_name, status=status)



