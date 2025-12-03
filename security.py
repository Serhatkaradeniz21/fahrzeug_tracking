"""
Dieses Modul wurde in der ersten Entwicklungsphase erstellt, um grundlegende Sicherheitsmechanismen
für das FahrzeugTracking-System zu implementieren. Es umfasst:

1. Passwort-Hashing und -Validierung (bcrypt):
   - Sicherstellung, dass Passwörter niemals im Klartext gespeichert werden.
   - Validierung von Passwörtern gegen gespeicherte Hashes.

2. CSRF-Schutz:
   - Generierung und Validierung von CSRF-Tokens, um Cross-Site-Request-Forgery-Angriffe zu verhindern.

3. Eingabevalidierung:
   - Überprüfung von Benutzereingaben wie Namen, Kilometerständen und Benutzernamen.

4. Sanitizing:
   - Entfernen gefährlicher Zeichen aus Benutzereingaben, um Sicherheitsrisiken zu minimieren.

5. Sichere Log-Ausgabe:
   - Vorbereitung von Log-Nachrichten, um sensible Daten zu schützen.
"""

# security.py
# Sicherheitsmodul für das FahrzeugTracking-System.
#
# Ziel:
# - Validierung von Benutzereingaben.
# - Sichere Speicherung von Passwörtern.
# - Schutz vor CSRF-Angriffen.
#
# Enthaltene Funktionen:
# - erstelle_passwort_hash: Erstellt sichere Passwort-Hashes.
# - pruefe_passwort: Validiert Passwörter gegen gespeicherte Hashes.
# - erzeuge_csrf_token: Generiert CSRF-Tokens.
# - signiere_csrf_token: Signiert CSRF-Tokens.
# - pruefe_signierten_csrf_token: Validiert signierte CSRF-Tokens.

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

# Lädt Umgebungsvariablen aus der .env-Datei
load_dotenv()

# ---------------------------------------------------------
# SYSTEMKONFIGURATION
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
# PASSWORT-SICHERHEIT
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
# CSRF-SCHUTZ (Token + Signatur)
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
    signatur = mac.hexdigest() # Hexadezimale Darstellung der Signatur
    return f"{roher_token}.{signatur}"


def pruefe_signierten_csrf_token(signierter_token: str) -> bool:
    """
    Überprüft die Gültigkeit eines signierten CSRF-Tokens.
    """
    try:
        roher_token, signatur = signierter_token.split(".", 1)
    except ValueError:
        return False
    mac = hmac.new(GEHEIMER_SCHLUESSEL.encode(), roher_token.encode(), hashlib.sha256)
    erwartete_signatur = mac.hexdigest()
    return hmac.compare_digest(signatur, erwartete_signatur)


# ---------------------------------------------------------
# EINGABEVALIDIERUNG
# ---------------------------------------------------------

def ist_name_gueltig(name: str) -> bool:
    """
    Überprüft, ob ein Name gültig ist (z. B. Fahrername).
    """
    if not name or len(name) > 100:
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
# SANITIZING
# ---------------------------------------------------------

def reinige_text_einfach(text: str) -> str:
    """
    Entfernt gefährliche Zeichen und escaped HTML.
    """
    if text is None:
        return ""
    text = text.strip()
    text = "".join(z for z in text if z.isprintable())# Entfernt nicht-druckbare Zeichen
    return html.escape(text)


def kuerze_text(text: str, maximale_laenge: int = 255) -> str:
    """
    Kürzt Texte, die zu lang sind.
    """
    text = text or ""
    return text[:maximale_laenge] if len(text) > maximale_laenge else text


# ---------------------------------------------------------
# SICHERE LOG-AUSGABE
# ---------------------------------------------------------

def sichere_log_nachricht(nachricht: str) -> str:
    """
    Bereitet Texte für die Ausgabe in Logfiles vor.
    """
    nachricht = reinige_text_einfach(nachricht)
    return nachricht.replace("\n", " ").replace("\r", " ")
