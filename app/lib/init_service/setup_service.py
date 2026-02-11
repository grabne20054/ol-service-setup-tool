from lib import broadcast
from lib import service_pool
from lib.config_loader import ConfigLoader
from lib.update_rp_configs import UpdateRPConfigs
from lib.init_service.state import State
from lib.init_service.setup_initated import SetupInitiated
from lib.init_service.services_created import ServicesCreated
from lib.init_service.configs_created import ConfigsCreated
from lib.init_service.configs_loaded import ConfigsLoaded
from lib.init_service.tests_passed import TestsPassed
from lib.init_service.setup_failed import SetupFailed

class SetupService:
    def __init__(self, service_name: str, initial_state: State, callback_url: str = ""):
        self.service_name = service_name
        self.pool = service_pool.ServicePool(service_name=self.service_name)
        self.handler = broadcast.DiscoverManagerNodes()
        self.manager_node = self.handler.hostname
        self.callback_url = callback_url
        self.setState(initial_state)

    def create_service(self):
        service_counter = 0
        try:
            for service, config in self.pool.services.items():
                    res, err, exit_status = self.handler.execute_command(
                        f"sudo docker service create --name {self.get_final_name(service)} "
                        f"--replicas {config.get('replicas', 1)} "
                        f"{' '.join([f'--env {env}' for env in config.get('env', [])])} "
                        f"--network {config.get('network', 'ingress')} "
                        f"{config['image']}"
                    )
                    if err or exit_status != 0:
                        raise Exception(f"Failed to create service {service}: {err} / Exit Status: {exit_status}")
                    elif res:
                        print(f"Service creation output for {service}: {res} / Exit Status: {exit_status}")
                        service_counter += 1
            if service_counter == len(self.pool.services):
                self.setState(ServicesCreated())
            else:
                self.setState(SetupFailed("Not all services were created successfully."))
        except Exception as e:
            self.setState(SetupFailed(str(e)))
            print(f"Error during service creation: {e}")

    def create_config(self):
        try:
            config_loader = ConfigLoader("./lib/globalrp_conf/configs", self.pool, self.handler, self.service_name)
            res = config_loader.load()

            if res is not None:
                self.setState(ConfigsCreated())
        except Exception as e:
            self.setState(SetupFailed(str(e)))
            print(f"Error during config creation: {e}")

    def update_rp_configs(self):
        try:
            update_rp_configs = UpdateRPConfigs(self.handler, self.service_name)
            update_rp_configs.mount_config()
            #update_rp_configs.clear_local_configs()
            self.setState(ConfigsLoaded())
        except Exception as e:
            self.setState(SetupFailed(str(e)))
            print(f"Error during RP config update: {e}")

    def mock_service_initialization(self):
        print("Mock initializing services...")
        self.setState(SetupInitiated())
        print(self.state)
        print("Mock loading configurations...")
        self.setState(ConfigsCreated())
        print(self.state)
        print("Mock updating RP configurations...")
        self.setState(ConfigsLoaded())
        print(self.state)
        print("Mock running service tests...")
        self.setState(TestsPassed())
        print(self.state)

    def get_final_name(self, image_name: str) -> str:
        return self.service_name + "-" + image_name
    
    def setState(self, state: State):
        self.state = state
        self.state.setContext(self)
        self.state._handle()

    def run(self):
        self.create_service()
        if isinstance(self.state, ServicesCreated):
            self.create_config()
        if isinstance(self.state, ConfigsCreated):
            self.update_rp_configs()
        print(f"Final state after setup: {self.state.__class__.__name__}")

        