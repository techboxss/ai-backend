from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    port: int = int(os.getenv("PORT", "8000"))
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    backend_base_url: str = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
    session_secret: str = os.getenv("SESSION_SECRET", "change-this-dev-secret")
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    google_redirect_uri: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2:latest")

settings = Settings()
