# hauptprogramm.py
# Einstiegspunkt der Anwendung.

from dotenv import load_dotenv
load_dotenv()  # <- ENV wird früh geladen, bevor irgendwas anderes passiert

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from controller.km_controller import router as km_router

app = FastAPI(
    title="FahrzeugTracking",
    description="Kilometer- und Wartungsverwaltung",
    version="1.0.0",
)

# Session-Middleware für Login und CSRF
app.add_middleware(
    SessionMiddleware,
    secret_key="session-geheim-serhat-123",
)

# Routen aus dem Kilometer-Controller
app.include_router(km_router)

# Statische Dateien (z. B. CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Upload-Verzeichnis für Fahrerfotos
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
