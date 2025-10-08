import sshclient
from dotenv import load_dotenv
import os
import redis
import time
import random


load_dotenv()

CACHE_SERVICE_NAME = os.getenv("CACHE_SERVICE_NAME")
CACHE_TTL = 60*3


# TODO: encryption of ips in redis SHA256

class DiscoverManagerNodes(sshclient.SSHClient):
    
    def __init__(self):
        self.hostname = os.getenv("INIT_MASTER_NODE")
        super().__init__(self.hostname, "ol", "ol") # sichere Speicherung Zugangsdaten?
        print(f"Initial connection to {self.hostname}")
        self.connect()

    def __get_manager_nodes(self) -> list[str]:
        master_nodes_ids = []
        command = "sudo docker node ls --format '{{.ID}}' --filter role=manager"
        output = self.execute_command(command)
        master_nodes_ids = output.splitlines()
        return master_nodes_ids

    def __get_manager_nodes_ips(self) -> list[str]:
        master_nodes_ids = self.__get_manager_nodes()
        ips = []

        for node_id in master_nodes_ids:
            command = "sudo docker node inspect " + str(node_id) + " --format '{{.Status.Addr}}'"
            output = self.execute_command(command)
            ip = output.strip()
            ips.append(ip)

        return ips
    
    def __decode_ips(self, ips: list[str]) -> str:
        decoded_ips = ','.join(ips)
        return decoded_ips

    def __encode_ips(self, decoded_ips: str) -> list[str]:
        return decoded_ips.split(',')

    def __update_cache_with_manager_nodes(self):
        try:
            ips = self.__get_manager_nodes_ips()
            decoded_ips = self.__decode_ips(ips)
            ips = decoded_ips
            r = redis.Redis(host=CACHE_SERVICE_NAME, port=6379, decode_responses=True) # service name!
            r.set('manager_nodes', ips)
            r.close()
        except Exception as e:
            print("Error updating Redis with manager nodes:", e)

    def __clear_cache(self):
        try:
            r = redis.Redis(host=CACHE_SERVICE_NAME, port=6379, decode_responses=True) # service name!
            r.delete('manager_nodes')
            r.close()
            print("Cleared Redis cache.")
        except Exception as e:
            print("Error clearing Redis:", e)

    def __check_cache(self) -> bool:
        try:
            r = redis.Redis(host=CACHE_SERVICE_NAME, port=6379, decode_responses=True) # service name!
            cached_value = r.get('manager_nodes')
            r.close()
            return cached_value is not None
        except Exception as e:
            print("Error checking Redis cache:", e)
            return False

    def __choose_connector(self) -> None:
        if self.__check_cache():
            r = redis.Redis(host=CACHE_SERVICE_NAME, port=6379, decode_responses=True) # service name!
            cached_value = r.get('manager_nodes')
            r.close()
            ips = self.__encode_ips(cached_value)
            chosen_ip = random.choice(ips)
            self.hostname = chosen_ip
        else:
            ips = self.__get_manager_nodes_ips()
            chosen_ip = random.choice(ips)
            self.hostname = chosen_ip

    def perform_health_check(self):
        try:
            while True:
                self.__choose_connector()
                print(f"Connecting to {self.hostname}")
                self.__clear_cache()
                self.__update_cache_with_manager_nodes()
                print("Updated manager nodes in cache.")
                time.sleep(CACHE_TTL)
        except Exception as e:
            print(e)

test = DiscoverManagerNodes()
test.perform_health_check()