import json
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()


class ServicesConfigHandler:
    def __init__(self, service_name):
        self.key = os.getenv("CONFIG_SECRET_KEY")
        self.path = "./lib/service_configs/config.json.enc"
        self.service_name = service_name

    def decode_key(self):
        if self.key is None:
            raise Exception("NO KEY FOUND")

        return self.key.encode()
    
    def get_config(self):
        decoded_key = self.decode_key()
        cipher = Fernet(decoded_key)

        with open(self.path, "rb") as f:
            encrypted_data = f.read()

        decryted_data = cipher.decrypt(encrypted_data)

        config = json.loads(decryted_data)
        return config
    
    def prepare_config(self):
        data = self.get_config()
        return self.replace_placeholders(data)

    def replace_placeholders(self, obj):
        if isinstance(obj, dict):
            return {
                k: self.replace_placeholders(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            if len(obj) == 0:
                return obj
            return {
                self.replace_placeholders(i)
                for i in obj
            }
        elif isinstance(obj, set):
            return {
                self.replace_placeholders(i, self.service_name)
                for i in obj
            }
        elif isinstance(obj, str):
            return obj.replace("{self.service_name}", self.service_name)
        else: 
            return obj