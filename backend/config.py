import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'universidad_db')
    JWT_SECRET = os.getenv('JWT_SECRET', 'solo-desarrollo-cambiar-antes-de-publicar')
    JWT_HOURS = 1
    FRONTEND_ORIGIN = os.getenv('FRONTEND_ORIGIN', 'http://localhost:8000')
