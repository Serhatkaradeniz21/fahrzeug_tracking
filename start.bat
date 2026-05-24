@echo off
echo Fahrzeug Tracking System wird gestartet...
echo.

REM Prüfen ob .env Datei existiert
if not exist .env (
    echo FEHLER: .env Datei nicht gefunden!
    echo Bitte kopieren Sie .env.example zu .env und passen Sie die Konfiguration an.
    echo.
    pause
    exit /b 1
)

REM Prüfen ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert oder nicht im PATH gefunden.
    echo Bitte installieren Sie Python 3.8 oder hoeher von https://www.python.org/
    echo.
    pause
    exit /b 1
)

REM Prüfen ob requirements.txt existiert
if not exist requirements.txt (
    echo FEHLER: requirements.txt nicht gefunden!
    echo.
    pause
    exit /b 1
)

REM Prüfen ob Abhängigkeiten installiert sind
echo Pruefe ob alle Abhaengigkeiten installiert sind...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Abhaengigkeiten werden installiert...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo FEHLER beim Installieren der Abhaengigkeiten.
        echo.
        pause
        exit /b 1
    )
)

REM Prüfen ob Datenbank erreichbar ist
echo Pruefe Datenbankverbindung...
python -c "from datenbank.verbindung import get_db_verbindung; conn = get_db_verbindung(); print('Datenbankverbindung erfolgreich')" >nul 2>&1
if errorlevel 1 (
    echo WARNUNG: Datenbankverbindung konnte nicht hergestellt werden.
    echo Versuche Datenbank und Tabellen zu erstellen...
    echo.
    
    REM SQL-Skript ausführen
    mysql -u root -pMoabit21! < "sql/tabellen erstellen.sql"
    if errorlevel 1 (
        echo FEHLER: Konnte Datenbank nicht erstellen.
        echo Bitte führen Sie manuell aus: mysql -u root -p < sql/tabellen erstellen.sql
        echo.
        pause
        exit /b 1
    )
    echo Datenbank und Tabellen wurden erstellt.
    echo.
)

REM Server starten
echo.
echo Starte Server auf http://127.0.0.1:8000
echo Druecken Sie STRG+C um den Server zu stoppen.
echo.
uvicorn hauptprogramm:app --reload --host 0.0.0.0 --port 8000

pause
