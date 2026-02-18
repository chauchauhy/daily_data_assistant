import os
import dotenv

class EnvLoadUtil:

    @staticmethod
    def load_env(key: str, default: str = None):
        dotenv.load_dotenv()
        return os.getenv(key, "") if default is None else os.getenv(key, default)
        
    @staticmethod
    def get_env_config_dict() -> dict:
        dotenv.load_dotenv()
        config = {}
        for key, value in os.environ.items():
            config[key] = value

        return config
    