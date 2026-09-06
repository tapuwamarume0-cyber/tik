import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-me")
    PROXY_LIST = os.getenv("PROXIES", "").split(",") if os.getenv("PROXIES") else []
    
    MAX_DAILY_ACTIONS = int(os.getenv("MAX_DAILY_ACTIONS", "35"))
    MIN_DELAY = int(os.getenv("MIN_DELAY", "120"))
    MAX_DELAY = int(os.getenv("MAX_DELAY", "480"))
    LIKE_PROBABILITY = float(os.getenv("LIKE_PROBABILITY", "0.12"))
    FOLLOW_PROBABILITY = float(os.getenv("FOLLOW_PROBABILITY", "0.04"))