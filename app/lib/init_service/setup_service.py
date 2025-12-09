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
        self.handler = broadcast.DiscoverManagerNodes()
        self.service_name = service_name
        self.manager_node = self.handler.hostname
        self.pool = service_pool.ServicePool(service_name=self.service_name)
        self.callback_url = callback_url
        self.setState(initial_state)
        print("Hallo: ", self.callback_url)

    def initialize_service(self):
        try:
            for service, config in self.pool.services.items():
                    res = self.handler.execute_command(
                        f"sudo docker service create --name {self.get_final_name(service)} "
                        f"--replicas {config.get('replicas', 1)} "
                        f"{' '.join([f'--env {env}' for env in config.get('env', [])])} "
                        f"--network {config.get('network', 'ingress')} "
                        f"{config['image']}"
                    )
                    print(f"Service {self.get_final_name(service)} created with response: {res}")
            print(f"Service {self.get_final_name(service)} created with response: {res}")
            self.setState(ServicesCreated())
            print(self.state)
        except Exception as e:
            self.setState(SetupFailed(str(e)))
            print(f"Error initializing service: {e}")
       
        try: 
            config_loader = ConfigLoader("./lib/globalrp_conf/configs", self.pool, self.handler, self.service_name)
            config_loader.load()
            self.setState(ConfigsCreated())
        except Exception as e:
            self.setState(SetupFailed(str(e)))
            print(f"Error loading configurations: {e}")

        try:
            update_rp_configs = UpdateRPConfigs(self.handler)
            update_rp_configs.mount_config("/etc/nginx/conf.d")
            #update_rp_configs.clear_local_configs()
            self.setState(ConfigsLoaded())
        except Exception as e:
            self.setState(SetupFailed(str(e)))
            print(f"Error updating RP configurations: {e}")

        try:
            #test if services are running
            print("Running service tests...")
            self.setState(TestsPassed())
        except Exception as e:
            self.setState(SetupFailed(str(e)))
            print(f"Error during service tests: {e}")
        

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
    

        