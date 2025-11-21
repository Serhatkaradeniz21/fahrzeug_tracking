# datenbank/verbindung.py
# Stellt die Verbindung zur MySQL-Datenbank her.
# Sensible Zugangsdaten werden aus einer .env-Datei geladen.

import os
import mysql.connector
from dotenv import load_dotenv  # Stelle sicher: pip install python-dotenv

# .env-Datei einlesen (nur einmal beim Start)
load_dotenv()


def get_db_verbindung():
    """
    Stellt eine Verbindung zur MySQL-Datenbank her.
    Die Zugangsdaten werden aus Umgebungsvariablen gelesen.
    Für die lokale Entwicklung greifen Default-Werte.
    """

    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "3306"))
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    database = os.getenv("DB_NAME", "fahrzeug_tracking")

    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        autocommit=True,
    )
