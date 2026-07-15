from dotenv import load_dotenv
import os

load_dotenv()

class Settings:

    APP_NAME = os.getenv("APP_NAME")

    DEBUG = os.getenv("DEBUG")

    DATABASE_URL = os.getenv("DATABASE_URL")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


settings = Settings()