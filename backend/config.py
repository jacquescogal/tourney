import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    instance = None
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "local")
        if self.environment == "production"  or self.environment == "staging":
            self.database_url = os.getenv("AWS_DATABASE_URL")
            self.redis_url = os.getenv("LOCAL_REDIS_URL")
        else:
            self.database_url = os.getenv("LOCAL_DATABASE_URL")
            self.redis_url = os.getenv("LOCAL_REDIS_URL")
        self.round_qualify_count ={
            1: int(os.getenv("ROUND_1_QUALIFY_COUNT", 4)),
            2: int(os.getenv("ROUND_2_QUALIFY_COUNT", 1)),
            3: int(os.getenv("ROUND_3_QUALIFY_COUNT", 1))
        }
        
    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = Settings()
        return cls.instance