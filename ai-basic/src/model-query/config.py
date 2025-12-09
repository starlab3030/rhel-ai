import os

from dotenv import load_dotenv

load_dotenv()

MODEL_URL = os.getenv("MODEL_URL")
DB_CONN_STRING = os.getenv("DB_CONN_STRING")