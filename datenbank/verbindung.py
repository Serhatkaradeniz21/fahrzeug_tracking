# datenbank/verbindung.py
# Stellt die Verbindung zur MySQL-Datenbank her.
#
# Ziel:
# - Laden sensibler Zugangsdaten aus der .env-Datei.
# - Aufbau einer sicheren Verbindung zur Datenbank.
#
# Enthaltene Funktionen:
# - get_db_verbindung: Erstellt eine Verbindung zur MySQL-Datenbank.

# Dieses Modul stellt die Verbindung zur MySQL-Datenbank her.
# Es lädt sensible Zugangsdaten aus einer .env-Datei und verwendet diese für die Verbindung.

import os
import mysql.connector
from dotenv import load_dotenv  # Stellt sicher, dass Umgebungsvariablen geladen werden

# .env-Datei einlesen (nur einmal beim Start)
load_dotenv()


def get_db_verbindung():
    """
    Stellt eine Verbindung zur MySQL-Datenbank her.

    Wichtige Punkte:
    - Die Zugangsdaten (Host, Port, Benutzer, Passwort, Datenbankname) werden aus Umgebungsvariablen geladen.
    - Standardwerte werden verwendet, falls keine Umgebungsvariablen gesetzt sind.
    - Die Verbindung wird mit `autocommit=True` erstellt, was bedeutet, dass Änderungen sofort in der Datenbank gespeichert werden.

    Rückgabewert:
    - Gibt ein `mysql.connector.connect`-Objekt zurück, das für Datenbankoperationen verwendet werden kann.
    """
    # Datenbankkonfigurationswerte aus Umgebungsvariablen laden
    host = os.getenv("DB_HOST", "localhost")  # Standard: localhost
    port = int(os.getenv("DB_PORT", "3306"))  # Standard: 3306 (MySQL-Standardport)
    user = os.getenv("DB_USER", "root")  # Standardbenutzer: root
    password = os.getenv("DB_PASSWORD", "")  # Standard: kein Passwort
    database = os.getenv("DB_NAME", "fahrzeug_tracking")  # Standarddatenbankname

    # Verbindung zur MySQL-Datenbank herstellen
    return mysql.connector.connect(
        host=host,  # Zielhost der Datenbank
        port=port,  # Zielport der Datenbank
        user=user,  # Benutzername für die Authentifizierung
        password=password,  # Passwort für die Authentifizierung
        database=database,  # Name der zu verwendenden Datenbank
        autocommit=True,  # Automatisches Speichern von Änderungen aktivieren
    )
