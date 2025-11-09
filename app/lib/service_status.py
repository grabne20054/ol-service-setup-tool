from lib.rcache.connector import RedisCacheConnector
import os

from dotenv import load_dotenv
load_dotenv()

CACHE_SERVICE_NAME = os.getenv("CACHE_SERVICE_NAME")

class ServiceStatus:
    def __init__(self, service_name: str):
        try:
            self.rcache_client = RedisCacheConnector(host=CACHE_SERVICE_NAME).get_client()
            print(f"Successfully connected to Redis at {CACHE_SERVICE_NAME}")
        except Exception as e:
            print(f"Failed to connect to Redis at {CACHE_SERVICE_NAME}: {e}")
            self.rcache_client = None
        self.service_name = service_name

    def get_status(self) -> str:
        if self.rcache_client:
            status = self.rcache_client.get(f"{self.service_name}")
            return status if status else "unknown"
        return "unknown"