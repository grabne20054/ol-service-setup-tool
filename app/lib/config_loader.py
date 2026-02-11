import os 
from lib import broadcast
from lib.service_configs import handler

# service_name --> hashed

class ConfigLoader:
    def __init__(self, config_path, pool: handler.ServicesConfigHandler, handler: broadcast.DiscoverManagerNodes, service_name: str):
        self.config_path = config_path
        self.pool = pool.prepare_config()
        self.handler = handler
        self.service_name = service_name

    def prepare_configs(self):
        os.makedirs(self.config_path, exist_ok=True)

        template_path = os.path.join(self.config_path, "template.conf")
        if not os.path.exists(template_path):
            raise FileNotFoundError("Template configuration file not found.")
        
        with open(template_path, 'r') as f:
            template_content = f.read()

        configs = []

        for service_type, service_info in self.pool.services.items():
            if service_type in ["at-fe", "ws-fe"]:
                upstream_name = f"{self.service_name}-{service_type}"
                port = service_info.get("ports", "").split(":")[0]

                config_content = (
                template_content
                .replace("$service_name", self.service_name)
                .replace("$upstream_name", upstream_name)
                .replace("$service_type", service_type)
                .replace("$port", port)
                )

                configs.append(config_content)

        with open(os.path.join(self.config_path, self.service_name + ".conf"), 'w') as f:
            f.write("\n\n".join(configs))

    ## deprecated
    def append_location_section(self, location_section: str):
        server_template_path = os.path.join(self.config_path, "server-template.conf")

        if not os.path.exists(server_template_path):
            raise FileNotFoundError("server-template.conf missing")

        with open(server_template_path, "r") as f:
            server_template = f.read()

            final_config_fragment = server_template.replace("$location_sections", location_section)
            output_path = os.path.join(self.config_path, "nginx-server.conf")

            if os.path.exists(output_path):
                with open(output_path, "r") as out_f:
                    existing = out_f.read()

                insert_at = existing.rfind('}')
                if insert_at != -1:
                    new_content = existing[:insert_at].rstrip() + "\n\n" + location_section + "\n\n" + existing[insert_at:]
                    with open(output_path, "w") as out_f:
                        out_f.write(new_content)
                else:
                    with open(output_path, "a") as out_f:
                        out_f.write("\n\n" + final_config_fragment + "\n")
            else:
                with open(output_path, "w") as out_f:
                    out_f.write(final_config_fragment)

            server_template = ""

    def check_existing_local_config(self,):
        config_file_path = os.path.join(self.config_path, self.service_name + ".conf")
        return os.path.exists(config_file_path)

    def create_config_on_host(self):
        local_path = os.path.join(self.config_path, self.service_name + ".conf")
        remote_path = "/tmp/" + self.service_name + ".conf"
        self.handler.transfer_file(local_path, remote_path)

        config_name = self.service_name + ".conf"

        try:
            res_rm = self.handler.execute_command(f"sudo docker config rm {config_name}")
            print(f"Existing Docker config removed for {config_name}: {res_rm}")
        except Exception as e:
            print(f"No existing Docker config to remove for {config_name}: {e}")

        res = self.handler.execute_command(f"sudo docker config create {config_name} {remote_path}")
        print(f"Docker config created for {config_name}: {res}")

        return config_name

    def clear_remote_config(self):
        try:
            res = self.handler.execute_command("sudo docker config rm " + self.service_name + "_" + self.service_type)
            print(f"Docker config removed for {self.service_name}-{self.service_type}: {res}")
        except Exception as e:
            print(f"Error removing Docker config for {self.service_name}-{self.service_type}: {e}")

    def clear_local_config(self):
        config_file_path = os.path.join(self.config_path, self.service_name + ".conf")
        if os.path.exists(config_file_path):
            os.remove(config_file_path)
            print(f"Local configuration file {config_file_path} removed.")
        else:
            print(f"No local configuration file found at {config_file_path} to remove.")

    def load(self):
        self.prepare_configs()
        res = self.create_config_on_host()
        if res is not None:
            self.handler.rcache_client.set(f"{self.service_name}", "Config loaded")
        #self.clear_local_config()
        return res

