import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
    AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
    AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
    AZURE_REDIRECT_URI = os.getenv("AZURE_REDIRECT_URI")
    AZURE_AUTHORITY = os.getenv("AZURE_AUTHORITY")

DB_CONFIG = {
    'server': os.getenv("AZURE_SQL_SERVER"),
    'database': os.getenv("AZURE_SQL_DATABASE"),
    'username': os.getenv("AZURE_SQL_USER"),
    'password': os.getenv("AZURE_SQL_PASSWORD"),
    'driver': os.getenv("AZURE_SQL_DRIVER"),
}