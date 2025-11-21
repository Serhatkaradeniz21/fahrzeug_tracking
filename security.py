# security.py
# Dieses Modul enthält alle sicherheitsrelevanten Funktionen für das FahrzeugTracking-System.
# Es stellt sicher, dass Benutzereingaben validiert, Passwörter sicher gespeichert und CSRF-Angriffe verhindert werden.

# Zentrale Sicherheitsfunktionen für das FahrzeugTracking-System.
# Beinhaltet Passwort-Hashing, Login-Validierung,
# CSRF-Schutz, Eingabevalidation, Sanitizing und sichere Log-Ausgabe.

import os  
import secrets 
import hmac 
import hashlib 
import html 
import re
from typing import Optional

import bcrypt
from dotenv import load_dotenv

# .env einlesen
load_dotenv()

# ---------------------------------------------------------
# SYSTEMKONFIGURATION
# ---------------------------------------------------------

# Geheimschlüssel für HMAC-Signaturen (CSRF, Token).
# Wird korrekt aus SECRET_KEY geladen.
GEHEIMER_SCHLUESSEL = os.getenv("SECRET_KEY")

if GEHEIMER_SCHLUESSEL is None:
    print("WARNUNG: SECRET_KEY NICHT gefunden! Fallback wird verwendet.")
    GEHEIMER_SCHLUESSEL = "fallback-key-1234567890"

# Disponentenzugang aus .env
DISPONENT_BENUTZERNAME = os.getenv("DISPONENT_BENUTZERNAME", "disponent")
_DISPONENT_PASSWORT_KLARTEXT = os.getenv("DISPONENT_PASSWORT", "Dispo123!")


# Der geheime Schlüssel wird aus der Umgebungsvariable `SECRET_KEY` geladen.
# Falls kein Schlüssel gefunden wird, wird ein Fallback-Schlüssel verwendet.
# WARNUNG: Der Fallback-Schlüssel sollte in einer Produktionsumgebung nicht verwendet werden.

# Die Zugangsdaten für den Disponenten werden aus der `.env`-Datei geladen.
# Standardwerte werden verwendet, falls keine Umgebungsvariablen gesetzt sind.

# ---------------------------------------------------------
# PASSWORT-HASHING (bcrypt)
# ---------------------------------------------------------

def erstelle_passwort_hash(roh_passwort: str) -> str:
    """
    Erzeugt einen sicheren bcrypt-Hash aus einem Klartextpasswort.
    
    """
    passwort_bytes = roh_passwort.encode("utf-8")
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(passwort_bytes, salt)
    return hash_bytes.decode("utf-8")


def pruefe_passwort(roh_passwort: str, gespeicherter_hash: str) -> bool:
    """
    Vergleicht ein eingegebenes Passwort mit dem gespeicherten Hash.
    """
    try:
        return bcrypt.checkpw(
            roh_passwort.encode("utf-8"),
            gespeicherter_hash.encode("utf-8")
        )
    except Exception:
        return False


# Der Hash des Disponenten wird beim Laden nur einmal berechnet.
_DISPONENT_PASSWORT_HASH = erstelle_passwort_hash(_DISPONENT_PASSWORT_KLARTEXT)


def pruefe_login(benutzername: str, passwort_klartext: str) -> bool:
    """
    Validiert den Disponenten-Login.
    Benutzername muss exakt passen,
    Passwort wird per bcrypt geprüft.
    """
    if benutzername != DISPONENT_BENUTZERNAME:
        return False

    return pruefe_passwort(passwort_klartext, _DISPONENT_PASSWORT_HASH)


# ---------------------------------------------------------
# CSRF-SCHUTZ (Token + Signatur)
# ---------------------------------------------------------

def erzeuge_csrf_token() -> str:
    """
    Erzeugt einen zufälligen CSRF-Token.
    """
    return secrets.token_urlsafe(32)


def signiere_csrf_token(roher_token: str) -> str:
    """
    Signiert den CSRF-Token mit HMAC-SHA256.
    Format: <token>.<signatur>
    """
    mac = hmac.new(
        GEHEIMER_SCHLUESSEL.encode(),
        roher_token.encode(),
        hashlib.sha256
    )
    signatur = mac.hexdigest()
    return f"{roher_token}.{signatur}"


def pruefe_signierten_csrf_token(signierter_token: str) -> bool:
    """
    Prüft Integrität und Echtheit eines signierten CSRF-Tokens.
    """
    try:
        roher_token, signatur = signierter_token.split(".", 1)
    except ValueError:
        return False

    mac = hmac.new(
        GEHEIMER_SCHLUESSEL.encode(),
        roher_token.encode(),
        hashlib.sha256
    )
    erwartete_signatur = mac.hexdigest()

    # Zeitkonstante Prüfung gegen Timing-Angriffe
    return hmac.compare_digest(signatur, erwartete_signatur)


# ---------------------------------------------------------
# EINGABEVALIDIERUNG (Name, Benutzername, Kilometer)
# ---------------------------------------------------------

def ist_name_gueltig(name: str) -> bool:
    """
    Validiert einen Fahrernamen.
    Erlaubt: Buchstaben, Zahlen, Leerzeichen, Punkt, Bindestrich.
    """
    if not name or len(name) > 100:
        return False

    muster = r"^[a-zA-ZäöüÄÖÜß0-9\s.\-]+$"
    return re.match(muster, name) is not None


def ist_kilometerstand_gueltig(wert: int) -> bool:
    """
    Prüft vernünftige KM-Werte.
    """
    if wert < 0:
        return False
    if wert > 2_000_000:
        return False
    return True


def ist_benutzername_gueltig(benutzername: str) -> bool:
    """
    Validiert den Benutzernamen (Disponent).
    """
    if not benutzername or len(benutzername) > 50:
        return False

    muster = r"^[a-zA-Z0-9_.\-]+$"
    return re.match(muster, benutzername) is not None


# ---------------------------------------------------------
# SANITIZING
# ---------------------------------------------------------

def reinige_text_einfach(text: str) -> str:
    """
    Entfernt gefährliche Zeichen und escaped HTML.
    Schutz gegen einfache XSS-Versuche.
    """
    if text is None:
        return ""

    # Rand-Leerzeichen entfernen
    text = text.strip()

    # Nicht druckbare Zeichen entfernen
    text = "".join(z for z in text if z.isprintable())

    # HTML escapen
    return html.escape(text)


def kuerze_text(text: str, maximale_laenge: int = 255) -> str:
    """
    Schneidet ungewöhnlich lange Eingaben ab.
    """
    text = text or ""
    return text[:maximale_laenge] if len(text) > maximale_laenge else text


# ---------------------------------------------------------
# SICHERE LOG-AUSGABE
# ---------------------------------------------------------

def sichere_log_nachricht(nachricht: str) -> str:
    """
    Bereitet Nutzereingaben für Logfiles auf,
    um Log-Injection und unlesbare Zeilen zu verhindern.
    """
    nachricht = reinige_text_einfach(nachricht)
    return nachricht.replace("\n", " ").replace("\r", " ")
