import os
import sys

# Ensure Python knows where to find our backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from configs.config import settings
from routes.health_routes import router as health_router
from routes.auth_routes import router as auth_router
from routes.gmail_routes import router as gmail_router
from routes.triage_routes import router as triage_router

app = FastAPI(title="LegalEase FastAPI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai-fronend-89.vercel.app",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(gmail_router)
app.include_router(triage_router)

