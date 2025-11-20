import os
from dotenv import load_dotenv

load_dotenv()  # load .env if present

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    RESULT_FOLDER = os.path.join(BASE_DIR, "static", "results")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///" + os.path.join(BASE_DIR, "database", "app.db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
