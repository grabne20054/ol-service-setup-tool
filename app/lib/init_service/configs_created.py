from lib.init_service.state import State
class SetupService:
    pass

class ConfigsCreated(State):
    def setContext(self, context: SetupService):
        self.context = context

    def handle(self):
        self.context.handler.rcache_conn.set(self.context.service_name, "configs successfully created")
