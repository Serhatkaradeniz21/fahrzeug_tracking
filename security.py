"""
# Sicherheitsmodul für das FahrzeugTracking-System

## Enthaltene Funktionen:

### 1. Systemkonfiguration
- `GEHEIMER_SCHLUESSEL`: Geheimschlüssel für HMAC-Signaturen.
- `DISPONENT_BENUTZERNAME`: Standardbenutzername für den Disponenten.
- `_DISPONENT_PASSWORT_HASH`: Gehashter Standardwert für das Passwort.

### 2. Passwort-Sicherheit
- `erstelle_passwort_hash`: Erstellt sichere Passwort-Hashes.
- `pruefe_passwort`: Validiert Passwörter gegen gespeicherte Hashes.
- `pruefe_login`: Prüft die Login-Daten des Disponenten.

### 3. CSRF-Schutz
- `erzeuge_csrf_token`: Generiert zufällige CSRF-Tokens.
- `signiere_csrf_token`: Signiert CSRF-Tokens mit HMAC-SHA256.
- `pruefe_signierten_csrf_token`: Überprüft die Gültigkeit eines signierten CSRF-Tokens.

### 4. Eingabevalidierung
- `ist_name_gueltig`: Überprüft, ob ein Name gültig ist.
- `ist_kilometerstand_gueltig`: Validiert Kilometerstände.
- `ist_benutzername_gueltig`: Überprüft, ob ein Benutzername gültig ist.

### 5. Sanitizing
- `reinige_text_einfach`: Entfernt gefährliche Zeichen und escaped HTML.
- `kuerze_text`: Kürzt Texte auf eine maximale Länge.

### 6. Sichere Log-Ausgabe
- `sichere_log_nachricht`: Bereitet Texte für Logfiles vor.

### 7. Session-Prüfung
- `ist_disponent_eingeloggt`: Prüft, ob ein Disponent eingeloggt ist.
"""

# security.py
# Sicherheitsmodul für das FahrzeugTracking-System.
# Dieses Modul enthält sicherheitsrelevante Funktionen für das FahrzeugTracking-System.
# Ziel ist es, Benutzereingaben zu validieren, Passwörter sicher zu speichern und CSRF-Angriffe zu verhindern.

import os
import secrets
import hmac
import hashlib
import html
import re
from typing import Optional

import bcrypt
from dotenv import load_dotenv
from fastapi import Request

# Lädt Umgebungsvariablen aus der .env-Datei
load_dotenv()

# ---------------------------------------------------------
#1 SYSTEMKONFIGURATION
# ---------------------------------------------------------

# Geheimschlüssel für HMAC-Signaturen (z. B. für CSRF-Tokens)
# Hinweis: In einer Produktionsumgebung sollte dieser Schlüssel sicher gespeichert werden.
# Ein Fallback-Wert wird verwendet, wenn kein SECRET_KEY gesetzt ist. Dies ist jedoch unsicher
# und sollte in einer Produktionsumgebung vermieden werden. Stattdessen sollte die Anwendung
# einen Fehler auslösen, wenn der Schlüssel fehlt.
GEHEIMER_SCHLUESSEL = os.getenv("SECRET_KEY")
if GEHEIMER_SCHLUESSEL is None:
    print("WARNUNG: SECRET_KEY NICHT gefunden! Fallback wird verwendet.")
    GEHEIMER_SCHLUESSEL = "fallback-key-1234567890"

# Zugangsdaten für den Disponenten aus der .env-Datei
DISPONENT_BENUTZERNAME = os.getenv("DISPONENT_BENUTZERNAME", "disponent")
_DISPONENT_PASSWORT_KLARTEXT = os.getenv("DISPONENT_PASSWORT", "Dispo123!")

# ---------------------------------------------------------
# 2 PASSWORT-SICHERHEIT
# ---------------------------------------------------------

def erstelle_passwort_hash(roh_passwort: str) -> str:
    """
    Erstellt einen sicheren Hash für ein Passwort.

    - Verwendet bcrypt, um sicherzustellen, dass die Passwörter nicht im Klartext gespeichert werden.
    - Der Hash wird mit einem zufälligen Salt generiert.
    """
    passwort_bytes = roh_passwort.encode("utf-8")
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(passwort_bytes, salt)
    return hash_bytes.decode("utf-8")


def pruefe_passwort(roh_passwort: str, gespeicherter_hash: str) -> bool:
    """
    Überprüft, ob ein eingegebenes Passwort mit einem gespeicherten Hash übereinstimmt.

    - Nutzt bcrypt, um die Sicherheit der Passwortprüfung zu gewährleisten.
    - Gibt True zurück, wenn das Passwort korrekt ist, andernfalls False.
    """
    try:
        return bcrypt.checkpw(roh_passwort.encode("utf-8"), gespeicherter_hash.encode("utf-8"))
    except Exception:
        return False


# Der Hash des Disponentenpassworts wird beim Laden des Moduls berechnet
_DISPONENT_PASSWORT_HASH = erstelle_passwort_hash(_DISPONENT_PASSWORT_KLARTEXT)


def pruefe_login(benutzername: str, passwort_klartext: str) -> bool:
    """
    Prüft, ob die eingegebenen Login-Daten korrekt sind.

    - Der Benutzername wird direkt mit dem gespeicherten verglichen.
    - Das Passwort wird mit dem gespeicherten Hash abgeglichen.
    """
    if benutzername != DISPONENT_BENUTZERNAME:
        return False
    return pruefe_passwort(passwort_klartext, _DISPONENT_PASSWORT_HASH)


# ---------------------------------------------------------
# 3 CSRF-SCHUTZ (Token + Signatur)
# ---------------------------------------------------------

def erzeuge_csrf_token() -> str:
    """
    Generiert einen zufälligen CSRF-Token.
    """
    return secrets.token_urlsafe(32)


def signiere_csrf_token(roher_token: str) -> str:
    """
    Signiert einen CSRF-Token mit HMAC-SHA256.

    - Für die Signatur wird ein geheimer Schlüssel (SECRET_KEY) verwendet.
    - Das Verfahren nutzt HMAC (Hash-based Message Authentication Code),
      um sicherzustellen, dass die Signatur eindeutig und manipulationssicher ist.
    - Der Hash ist durch die Kombination aus dem geheimen Schlüssel und dem Token einzigartig.
    """
    mac = hmac.new(GEHEIMER_SCHLUESSEL.encode(), roher_token.encode(), hashlib.sha256)
    signatur = mac.hexdigest()  # Hexadezimale Darstellung der Signatur
    return f"{roher_token}.{signatur}"


def pruefe_signierten_csrf_token(signierter_token: str) -> bool:
    """
    Überprüft die Gültigkeit eines signierten CSRF-Tokens.
    """
    try:
        roher_token, signatur = signierter_token.split(".", 1)
    except ValueError:
        return False
    # neue hmac signatur erstellen und vergleichen
    mac = hmac.new(GEHEIMER_SCHLUESSEL.encode(), roher_token.encode(), hashlib.sha256)
    erwartete_signatur = mac.hexdigest()
    return hmac.compare_digest(signatur, erwartete_signatur)


# ---------------------------------------------------------
# 4 EINGABEVALIDIERUNG
# ---------------------------------------------------------

def ist_name_gueltig(name: str) -> bool:
    """
    Überprüft, ob ein Name gültig ist (z. B. Fahrername).
    """
    if not name or len(name) > 50:
        return False
    muster = r"^[a-zA-ZäöüÄÖÜß0-9\s.\-]+$"
    return re.match(muster, name) is not None


def ist_kilometerstand_gueltig(wert: int) -> bool:
    """
    Validiert, ob ein Kilometerstand realistisch ist.
    """
    return 0 <= wert <= 2_000_000


def ist_benutzername_gueltig(benutzername: str) -> bool:
    """
    Überprüft, ob ein Benutzername gültig ist.
    """
    if not benutzername or len(benutzername) > 50:
        return False
    muster = r"^[a-zA-Z0-9_.\-]+$"
    return re.match(muster, benutzername) is not None


# ---------------------------------------------------------
# 5 SANITIZING
# ---------------------------------------------------------

def reinige_text_einfach(text: str) -> str:
    """
    Entfernt gefährliche Zeichen und escaped HTML.
    """
    if text is None:
        return ""
    text = text.strip()
    text = "".join(z for z in text if z.isprintable())  # Entfernt nicht-druckbare Zeichen
    return html.escape(text)


def kuerze_text(text: str, maximale_laenge: int = 255) -> str:
    """
    Kürzt Texte, die zu lang sind.
    """
    text = text or ""
    return text[:maximale_laenge] if len(text) > maximale_laenge else text


# ---------------------------------------------------------
# 6 SICHERE LOG-AUSGABE
# ---------------------------------------------------------

def sichere_log_nachricht(nachricht: str) -> str:
    """
    Bereitet Texte für die Ausgabe in Logfiles vor.
    """
    nachricht = reinige_text_einfach(nachricht)
    return nachricht.replace("\n", " ").replace("\r", " ")


# ---------------------------------------------------------
# 7 Session prüfen
# ---------------------------------------------------------

def ist_disponent_eingeloggt(request: Request) -> bool:
    """
    Prüft, ob in der aktuellen Sitzung ein Disponent eingeloggt ist.

    Diese Funktion kapselt den Zugriff auf die Session und wird z. B. vom
    Controller genutzt, um geschützte Bereiche (Dashboard, Fahrzeugverwaltung,
    Historie) abzusichern.
    """
    session = getattr(request, "session", None)
    if not session:
        return False
    return session.get("eingeloggt") is True
