from dotenv import load_dotenv
import os

# Load biến môi trường từ file .env (chỉ dùng cho môi trường development)
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///financial.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False