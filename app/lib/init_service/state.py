from abc import ABC, abstractmethod
from lib.webhook.send import send_webhook

class SetupService:
    pass

class State(ABC):
    
    @abstractmethod
    def setContext(self, context: SetupService):
        pass

    def _handle(self):
        send_webhook(
            self.context.callback_url,
            {"service_name": self.context.service_name, "state": str(self)}
        )
        return self.handle()
    
    @abstractmethod
    def handle(self):
        pass

    def __str__(self):
        return self.__class__.__name__