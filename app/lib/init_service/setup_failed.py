from lib.init_service.state import State

class SetupService:
    pass

class SetupFailed(State):

    def __init__(self, reason: str):
        super().__init__()
        self.reason = reason
        print(f"Setup failed due to: {self.reason}") # Future: LOG this properly

    def setContext(self, context: SetupService):
        self.context = context

    def handle(self):
        self.context.handler.rcache_conn.set(self.context.service_name, "setup failed")

    