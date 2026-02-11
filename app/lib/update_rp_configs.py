from lib.broadcast import DiscoverManagerNodes
import os

class UpdateRPConfigs:
    def __init__(self, handler: DiscoverManagerNodes, service_name: str, config_directory: str = "./lib/globalrp_conf/configs"):
        self.handler = handler
        self.config_directory = config_directory
        self.service_name = service_name

    def get_all_local_configs(self):
        configs = []
        for file_name in os.listdir(self.config_directory):
            if file_name.endswith(".conf") and not file_name.startswith("template"):
                configs.append(file_name)
        return configs

    def get_remote_config_by_service(self):
        output, res, exit_code = self.handler.execute_command("sudo docker config ls --format '{{.Name}}'")
        remote_configs = output.splitlines()
        return [config for config in remote_configs if config.startswith(self.service_name)]

    def remove_default_remote_configs(self, default_configs=["default.conf"]):
        for config_name in default_configs:
            try:
                res = self.handler.execute_command(f"sudo docker config rm {config_name}")
                print(f"Removed default remote config {config_name}: {res}")
            except Exception as e:
                print(f"Error removing default remote config {config_name}: {e}")

    def mount_config(self, config_remote_path="/etc/nginx/locations", service_name="globalrp"):
        config_flags = []

        os.makedirs(config_remote_path, exist_ok=True)

        for config_name in self.get_remote_config_by_service():
            target_path = f"{config_remote_path}/{config_name}"
            if not target_path.endswith(".conf"):
                target_path += ".conf"

            config_flags.append(
                f'--config-add source={config_name},target={target_path}'
            )

        cmd = f"sudo docker service update {' '.join(config_flags)} {service_name}"

        res = self.handler.execute_command(cmd)
        print(f"Updated service {service_name} with config files at {config_remote_path}: {res}")


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