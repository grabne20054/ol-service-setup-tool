from lib.config_loader import ConfigLoader
from lib.broadcast import DiscoverManagerNodes
import os

class UpdateRPConfigs:
    def __init__(self, handler: DiscoverManagerNodes, config_directory: str = "./lib/globalrp_conf/configs"):
        self.handler = handler
        self.config_directory = config_directory

    def get_all_local_configs(self):
        configs = []
        for file_name in os.listdir(self.config_directory):
            if file_name.endswith(".conf") and not file_name.startswith("template") and not file_name.startswith("server-template"):
                configs.append(file_name)
        return configs
    
    def mount_config(self, config_remote_path: str, service_name: str = "globalrp"):
        res = self.handler.execute_command(
            f"sudo docker service update "
            f"{' '.join([f'--config-add source={config_name},target={config_remote_path}/{config_name}' for config_name in self.get_all_local_configs()])} "
            f"{service_name}"
        )
        print(f"Updated service {service_name} with config {self.get_all_local_configs()} at {config_remote_path}: {res}")
        self.handler.rcache_client.set(f"{service_name}", "Configs mounted")

    def clear_local_configs(self):
        for file_name in self.get_all_local_configs():
            file_path = os.path.join(self.config_directory, file_name)
            os.remove(file_path)
            print(f"Removed local config file: {file_path}")

    def clear_remote_configs(self, service_name: str = "globalrp"):
        for config_name in self.get_all_local_configs():
            try:
                res = self.handler.execute_command(f"sudo docker config rm {config_name}")
                print(f"Removed remote config {config_name} from service {service_name}: {res}")
            except Exception as e:
                print(f"Error removing remote config {config_name} from service {service_name}: {e}")