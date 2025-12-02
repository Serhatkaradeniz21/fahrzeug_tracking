# hauptprogramm.py
# Einstiegspunkt der Anwendung. Hier wird die FastAPI-Anwendung konfiguriert und gestartet.
#
# Enthaltene Funktionen:
# - app: Initialisiert die FastAPI-Anwendung.
# - Middleware-Konfiguration: Fügt Sitzungs- und Sicherheits-Middleware hinzu.
# - Routenregistrierung: Bindet die Controller-Routen ein.
# - Statische Dateien: Stellt CSS und andere Ressourcen bereit.

# ---------------------------------------------------------
# Voraussetzungen vor dem Start:
# 1. Umgebungsvariablen:
#    - Eine .env-Datei muss vorhanden sein, die wichtige Konfigurationswerte enthält, wie z. B.:
#      SECRET_KEY, Datenbankverbindung, E-Mail-Konfiguration.
# 2. Verzeichnisstruktur:
#    - Die folgenden Verzeichnisse müssen existieren:
#      controller/, static/, uploads/.
# 3. Abhängigkeiten:
#    - Alle benötigten Python-Pakete (fastapi, python-dotenv, starlette) müssen installiert sein.
# 4. Datenbank:
#    - Die Datenbank muss eingerichtet sein, Tabellen und initiale Daten sollten vorhanden sein.
# 5. Serverstart:
#    - Der FastAPI-Server wird mit uvicorn gestartet: uvicorn hauptprogramm:app --reload
# ---------------------------------------------------------

from dotenv import load_dotenv
load_dotenv()  # Lädt Umgebungsvariablen aus der .env-Datei

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from controller.km_controller import router as km_router
from security import erzeuge_csrf_token  # Import für die CSRF-Token-Generierung

# Initialisierung der FastAPI-Anwendung
app = FastAPI(
    title="FahrzeugTracking",  # Titel der Anwendung
    description="Verwaltung von Kilometer- und Wartungsdaten",  # Kurze Beschreibung
    version="1.0.0",  # Versionsnummer
)

# Middleware für Sitzungen (z. B. Login, CSRF-Schutz)
# Diese Middleware ermöglicht die Verwaltung von Sitzungen und schützt vor CSRF-Angriffen.
app.add_middleware(
    SessionMiddleware,
    secret_key="session-geheim-serhat-123",  # Geheimschlüssel für Sitzungen
)

# Kilometer-Routen einbinden
# Hier werden die Routen aus dem Modul km_controller registriert.
app.include_router(km_router)

# Statische Dateien bereitstellen
# Ermöglicht den Zugriff auf CSS-Dateien, Bilder und andere statische Ressourcen.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Upload-Verzeichnis bereitstellen
# Ermöglicht den Zugriff auf hochgeladene Dateien, wie z. B. Fahrerfotos.
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Standardmäßige CSRF-Token-Generierung (pro Sitzung ein Token)
def generiere_csrf_pro_sitzung(request):
    """
    Generiert einen CSRF-Token, der für die gesamte Sitzung gültig bleibt.

    - Der Token wird nur einmal pro Sitzung erstellt und in der Session gespeichert.
    - Wird für die Absicherung von Formularen gegen CSRF-Angriffe verwendet.
    """
    if "csrf_token" not in request.session:
        # security genutzt: CSRF-Token wird hier generiert und in der Sitzung gespeichert
        request.session["csrf_token"] = erzeuge_csrf_token()
    return request.session["csrf_token"]

# Hinweis: Die CSRF-Token-Generierung erfolgt standardmäßig pro Sitzung.
# Bei Bedarf kann die Methode zur CSRF-Token-Generierung angepasst werden,
# indem die Funktion `generiere_csrf_pro_sitzung` überschrieben oder erweitert wird.
