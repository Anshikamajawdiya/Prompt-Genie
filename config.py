import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY     = os.getenv("GEMINI_API_KEY", "")
    FLASK_ENV          = os.getenv("FLASK_ENV", "production")
    DEBUG              = os.getenv("FLASK_DEBUG", "False") == "True"
    PORT               = int(os.getenv("PORT", 5000))
    GEMINI_MODEL       = "gemini-2.0-flash"
    GEMINI_MAX_TOKENS  = 1024
    GEMINI_TEMPERATURE = 0.8
    FALLBACK_ENABLED   = True
    