# controller/km_controller.py
# HTTP-Routen und zugehörige Logik für Benutzerinteraktionen.
#
# Ziel:
# - Verbindung zwischen Service- und Präsentationsschicht.
# - Übergabe der richtigen Daten an Templates.
#
# Enthaltene Funktionen:
# - generiere_und_speichere_csrf: CSRF-Token-Management.
# - Login- und Logout-Management.
# - Dashboard- und Fahrzeugverwaltung.


#
#from datetime import date
#Wird verwendet, um Datumswerte zu verarbeiten (z. B. tuev_bis).
#from pathlib import Path
#Wird verwendet, um Dateipfade zu erstellen und zu verwalten (z. B. UPLOAD_DIR für das Speichern von Fotos).
#from typing import Optional
#Wird für Typannotationen verwendet, um anzugeben, dass ein Wert optional sein kann (z. B. foto_datei: Optional[UploadFile]).




from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse

from service.km_service import KilometerService
from view import templates
from model.km_model import KilometerEingabeRequest
from security import (
    erzeuge_csrf_token,
    signiere_csrf_token,
    pruefe_signierten_csrf_token,
    ist_benutzername_gueltig,
    ist_kilometerstand_gueltig,
    ist_name_gueltig,
    reinige_text_einfach,
    pruefe_login,
)

router = APIRouter()
service = KilometerService()

# Upload-Verzeichnis für Fotos
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------
# CSRF-Token-Management
# ---------------------------------------------------------

# Diese Funktion erzeugt einen CSRF-Token, signiert ihn und speichert ihn in der Sitzung.
# Der Token wird nur einmal pro Sitzung generiert und bleibt für die gesamte Sitzung gültig.
def generiere_und_speichere_csrf(request: Request) -> str:
    """
    Generiert einen neuen CSRF-Token, signiert ihn und speichert ihn in der Sitzung,
    falls noch keiner existiert.

    - Der Token wird für die gesamte Sitzung verwendet.
    - Die Signatur stellt sicher, dass der Token nicht manipuliert wurde.
    """
    if "csrf_token" not in request.session:
        # security genutzt: CSRF-Token wird hier generiert
        roher_token = erzeuge_csrf_token()
        # security genutzt: CSRF-Token wird hier signiert
        signierter_token = signiere_csrf_token(roher_token)
        request.session["csrf_token"] = signierter_token
    return request.session["csrf_token"]


# Diese Funktion überprüft die Gültigkeit eines empfangenen CSRF-Tokens.
# - Vergleicht den empfangenen Token mit dem in der Session gespeicherten Token.
# - Nutzt eine zeitkonstante Prüfung, um Timing-Angriffe zu verhindern.
def csrf_pruefen(request: Request, empfangener_token: str) -> bool:
    """
    Überprüft die Gültigkeit eines empfangenen CSRF-Tokens.

    - Vergleicht den empfangenen Token mit dem in der Session gespeicherten Token.
    - Nutzt eine zeitkonstante Prüfung, um Timing-Angriffe zu verhindern.
    """
    gespeicherter_token = request.session.get("csrf_token")

    if not gespeicherter_token:
        return False

    if gespeicherter_token != empfangener_token:
        return False

    # security genutzt: Überprüfung des CSRF-Tokens
    return pruefe_signierten_csrf_token(empfangener_token)


# ---------------------------------------------------------
# Login-Management
# ---------------------------------------------------------

# Überprüft, ob der Benutzer eingeloggt ist.
# - Gibt True zurück, wenn der Benutzer eingeloggt ist, andernfalls False.
def pruefe_login_erforderlich(request: Request) -> bool:
    """
    Überprüft, ob der Benutzer eingeloggt ist.

    - Gibt True zurück, wenn der Benutzer eingeloggt ist, andernfalls False.
    """
    return request.session.get("eingeloggt") is True


# Leitet den Benutzer auf die Login-Seite weiter, falls er nicht eingeloggt ist.
# - Verhindert den Zugriff auf geschützte Routen für nicht authentifizierte Benutzer.
def login_oder_redirect(request: Request):
    """
    Leitet den Benutzer auf die Login-Seite weiter, falls er nicht eingeloggt ist.

    - Verhindert den Zugriff auf geschützte Routen für nicht authentifizierte Benutzer.
    """
    # security genutzt: Überprüfung, ob Benutzer eingeloggt ist
    if not pruefe_login_erforderlich(request):
        return RedirectResponse(url="/login", status_code=302)
    return None


# ---------------------------------------------------------
# Login / Logout
# ---------------------------------------------------------

# 1. Login-Seite anzeigen (GET)
@router.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    """
    Zeigt die Login-Seite an und generiert einen neuen CSRF-Token.

    - Das Formular auf der Login-Seite verwendet diesen Token zur Absicherung.
    """
    csrf_token = generiere_und_speichere_csrf(request)
    return templates.render_login_seite(csrf_token=csrf_token)


# 2. Login-Daten verarbeiten (POST)
@router.post("/login", response_class=HTMLResponse)
def login_post(
    request: Request,
    benutzername: str = Form(...),
    passwort: str = Form(...),
    csrf_token: str = Form(...),
):
    """
    Verarbeitet die Login-Daten des Benutzers.

    - Überprüft den CSRF-Token, um sicherzustellen, dass die Anfrage legitim ist.
    - Validiert den Benutzernamen und das Passwort.
    - Setzt die Session-Variable "eingeloggt" auf True, wenn die Anmeldung erfolgreich ist.
    """
    if not csrf_pruefen(request, csrf_token):
        csrf_neu = generiere_und_speichere_csrf(request)
        return templates.render_login_seite(csrf_token=csrf_neu, fehlermeldung="Ungültiger CSRF-Token.")

    # security genutzt: Validierung des Benutzernamens
    if not ist_benutzername_gueltig(benutzername):
        neuer = generiere_und_speichere_csrf(request)
        return templates.render_login_seite(
            csrf_token=neuer,
            fehlermeldung="Benutzername ungültig.",
        )

    # security genutzt: Bereinigung des Benutzernamens
    benutzer = reinige_text_einfach(benutzername)
    # security genutzt: Überprüfung der Login-Daten
    if not pruefe_login(benutzer, passwort):
        neuer = generiere_und_speichere_csrf(request)
        return templates.render_login_seite(
            csrf_token=neuer,
            fehlermeldung="Login fehlgeschlagen.",
        )

    # Benutzer erfolgreich eingeloggt
    request.session["eingeloggt"] = True
    return RedirectResponse(url="/dashboard", status_code=302)


# 3. Logout (GET)
@router.get("/logout")
def logout(request: Request):
    """
    Meldet den Benutzer ab und leitet zur Login-Seite weiter.

    - Die Session wird vollständig geleert.
    - Der Benutzer wird auf die Login-Seite umgeleitet.
    """
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)


# ---------------------------------------------------------
# Dashboard-Management
# ---------------------------------------------------------

# 4. Dashboard anzeigen (GET)
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    """
    Zeigt das Dashboard des Disponenten an.

    - Überprüft, ob der Benutzer eingeloggt ist.
    - Lädt die Fahrzeugübersicht für das Dashboard.
    - Generiert einen neuen CSRF-Token für die Sicherheit.
    """
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung

    fahrzeuge = service.hole_fahrzeuge_fuer_dashboard()
    csrf_token = generiere_und_speichere_csrf(request) 
    return templates.render_dashboard(fahrzeuge, csrf_token=csrf_token)


# ---------------------------------------------------------
# Fahrzeug-Management
# ---------------------------------------------------------

# 5. Fahrzeug anlegen (GET und POST)
@router.get("/fahrzeug/neu", response_class=HTMLResponse)
def fahrzeug_neu_get(request: Request):
    """
    Zeigt das Formular zum Anlegen eines neuen Fahrzeugs an.

    - Stellt sicher, dass der Benutzer eingeloggt ist.
    - Generiert einen neuen CSRF-Token für die Formularsicherheit.
    """
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung

    csrf_token = generiere_und_speichere_csrf(request)
    return templates.render_fahrzeug_neu(csrf_token=csrf_token)


@router.post("/fahrzeug/neu", response_class=HTMLResponse)
def fahrzeug_neu_post(
    request: Request,
    kennzeichen: str = Form(...),
    bezeichnung: str = Form(...),
    aktueller_km_wert: str = Form(...),
    tuev_bis: date = Form(...),
    naechster_oelwechsel_km_wert: str = Form(...),
    csrf_token: str = Form(...),
):
    """
    Verarbeitet die Eingaben zum Anlegen eines neuen Fahrzeugs.

    - Überprüft den CSRF-Token, um Cross-Site-Request-Forgery zu verhindern.
    - Validiert die Benutzereingaben und speichert die Fahrzeugdaten.
    """
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung

    if not csrf_pruefen(request, csrf_token):
        return RedirectResponse(url="/dashboard", status_code=302)

    # Kilometerwerte prüfen & casten
    try:
        aktueller_km = int(aktueller_km_wert)
        naechster_oelwechsel_km = int(naechster_oelwechsel_km_wert)
    except ValueError:
        neuer = generiere_und_speichere_csrf(request)
        return templates.render_fahrzeug_neu(
            csrf_token=neuer,
            hinweis="Bitte nur ganze Zahlen bei Kilometerfeldern.",
        )

    service.erstelle_fahrzeug(
        kennzeichen=kennzeichen,
        bezeichnung=bezeichnung,
        aktueller_km=aktueller_km,
        tuev_bis=tuev_bis,
        naechster_oelwechsel_km=naechster_oelwechsel_km,
    )

    return RedirectResponse(url="/dashboard", status_code=302)


# ---------------------------------------------------------
# Fahrzeug anlegen / bearbeiten / löschen
# ---------------------------------------------------------

@router.get("/fahrzeug/neu", response_class=HTMLResponse)
def fahrzeug_neu_get(request: Request):
    """
    Zeigt das Formular zum Anlegen eines neuen Fahrzeugs an.

    - Stellt sicher, dass der Benutzer eingeloggt ist.
    - Generiert einen neuen CSRF-Token für die Formularsicherheit.
    """
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung

    csrf_token = generiere_und_speichere_csrf(request)
    return templates.render_fahrzeug_neu(csrf_token=csrf_token)


@router.post("/fahrzeug/neu", response_class=HTMLResponse)
def fahrzeug_neu_post(
    request: Request,
    kennzeichen: str = Form(...),
    bezeichnung: str = Form(...),
    aktueller_km_wert: str = Form(...),
    tuev_bis: date = Form(...),
    naechster_oelwechsel_km_wert: str = Form(...),
    csrf_token: str = Form(...),
):
    """
    Verarbeitet die Eingaben zum Anlegen eines neuen Fahrzeugs.

    - Überprüft den CSRF-Token, um Cross-Site-Request-Forgery zu verhindern.
    - Validiert die Benutzereingaben und speichert die Fahrzeugdaten.
    """
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung

    if not csrf_pruefen(request, csrf_token):
        return RedirectResponse(url="/dashboard", status_code=302)

    # Kilometerwerte prüfen & casten
    try:
        aktueller_km = int(aktueller_km_wert)
        naechster_oelwechsel_km = int(naechster_oelwechsel_km_wert)
    except ValueError:
        neuer = generiere_und_speichere_csrf(request)
        return templates.render_fahrzeug_neu(
            csrf_token=neuer,
            hinweis="Bitte nur ganze Zahlen bei Kilometerfeldern.",
        )

    service.erstelle_fahrzeug(
        kennzeichen=kennzeichen,
        bezeichnung=bezeichnung,
        aktueller_km=aktueller_km,
        tuev_bis=tuev_bis,
        naechster_oelwechsel_km=naechster_oelwechsel_km,
    )

    return RedirectResponse(url="/dashboard", status_code=302)


@router.get("/fahrzeug/{fahrzeug_id}/bearbeiten", response_class=HTMLResponse)
def fahrzeug_bearbeiten_get(request: Request, fahrzeug_id: int):
    """
    Zeigt das Formular zum Bearbeiten eines bestehenden Fahrzeugs an.

    - Stellt sicher, dass der Benutzer eingeloggt ist.
    - Lädt die Fahrzeugdetails für das Bearbeitungsformular.
    """
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung

    fahrzeug = service.hole_fahrzeug_details(fahrzeug_id)
    if not fahrzeug:
        return RedirectResponse(url="/dashboard", status_code=302)

    csrf_token = generiere_und_speichere_csrf(request)
    return templates.render_fahrzeug_bearbeiten(fahrzeug, csrf_token=csrf_token)


@router.post("/fahrzeug/{fahrzeug_id}/bearbeiten", response_class=HTMLResponse)
def fahrzeug_bearbeiten_post(
    request: Request,
    fahrzeug_id: int,
    kennzeichen: str = Form(...),
    bezeichnung: str = Form(...),
    aktueller_km_wert: str = Form(...),
    tuev_bis: date = Form(...),
    naechster_oelwechsel_km_wert: str = Form(...),
    csrf_token: str = Form(...),
):
    """
    Verarbeitet die Eingaben zum Bearbeiten eines bestehenden Fahrzeugs.

    - Überprüft den CSRF-Token für die Sicherheit.
    - Validiert die aktualisierten Benutzereingaben.
    - Speichert die Änderungen in der Fahrzeugdatenbank.
    """
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung

    if not csrf_pruefen(request, csrf_token):
        return RedirectResponse(url="/dashboard", status_code=302)

    try:
        aktueller_km = int(aktueller_km_wert)
        naechster_oelwechsel_km = int(naechster_oelwechsel_km_wert)
    except ValueError:
        fahrzeug = service.hole_fahrzeug_details(fahrzeug_id)
        neuer = generiere_und_speichere_csrf(request)
        return templates.render_fahrzeug_bearbeiten(
            fahrzeug=fahrzeug,
            csrf_token=neuer,
            hinweis="Bitte nur ganze Zahlen eingeben.",
        )

    service.aktualisiere_fahrzeug(
        fahrzeug_id=fahrzeug_id,
        kennzeichen=kennzeichen,
        bezeichnung=bezeichnung,
        aktueller_km=aktueller_km,
        tuev_bis=tuev_bis,
        naechster_oelwechsel_km=naechster_oelwechsel_km,
    )

    return RedirectResponse(url="/dashboard", status_code=302)


@router.post("/fahrzeug/{fahrzeug_id}/loeschen")
def fahrzeug_loeschen_post(
    request: Request,
    fahrzeug_id: int,
    csrf_token: str = Form(...),
):
    """
    Löscht ein Fahrzeug aus der Datenbank.

    - Überprüft den CSRF-Token für die Sicherheit.
    - Entfernt das Fahrzeug aus der Datenbank.
    - Leitet zurück zum Dashboard.
    """
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung

    if not csrf_pruefen(request, csrf_token):
        return RedirectResponse(url="/dashboard", status_code=302)

    service.loesche_fahrzeug(fahrzeug_id)
    return RedirectResponse(url="/dashboard", status_code=302)


# ---------------------------------------------------------
# KM-Anforderungen / Links
# ---------------------------------------------------------

@router.post("/km/anforderung/{fahrzeug_id}", response_class=HTMLResponse)
def km_anforderung_erzeugen(
    request: Request,
    fahrzeug_id: int,
    csrf_token: str = Form(...),
):
    """
    Erzeugt eine KM-Anforderung für ein Fahrzeug.

    - Überprüft, ob der Benutzer eingeloggt ist.
    - Generiert einen neuen CSRF-Token für die Anfrage.
    """
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung

    if not csrf_pruefen(request, csrf_token):
        return RedirectResponse(url="/dashboard", status_code=302)

    antwort = service.erzeuge_km_anforderung(fahrzeug_id)
    return templates.render_km_link_anzeige(antwort)


# ---------------------------------------------------------
# KM-Eingabe durch Fahrer
# ---------------------------------------------------------

@router.get("/km/eingabe/{token}", response_class=HTMLResponse)
def km_eingabe_formular_anzeigen(request: Request, token: str):
    """
    Zeigt das Formular zur Eingabe der Kilometerstände durch den Fahrer an.

    - Ermöglicht es Fahrern, ihre gefahrenen Kilometer einzugeben.
    - Bietet die Möglichkeit, ein Foto hochzuladen.
    """
    csrf_token = generiere_und_speichere_csrf(request)
    return templates.render_km_eingabe_formular(token, csrf_token=csrf_token)


@router.post("/km/eingabe/{token}", response_class=HTMLResponse)
def km_eingabe_absenden(
    request: Request,
    token: str,
    name_fahrer: str = Form(...),
    kilometerstand_wert: str = Form(...),
    csrf_token: str = Form(...),
    foto_datei: Optional[UploadFile] = File(None),
):
    """
    Verarbeitet die Eingabe des Kilometerstands durch den Fahrer.

    - Überprüft den CSRF-Token für die Sicherheit.
    - Validiert die Eingaben für Namen und Kilometerstand.
    - Speichert die Eingaben in der Datenbank.
    - Ermöglicht das Hochladen eines Fotos.
    """
    if not csrf_pruefen(request, csrf_token):
        neuer = generiere_und_speichere_csrf(request)
        return templates.render_km_eingabe_formular(
            token, csrf_token=neuer,
            hinweis="Sicherheitsfehler: Kilometer kleiner als aktuellen Kilometerstand.",
        )

    # security genutzt: Validierung des Fahrernamens
    if not ist_name_gueltig(name_fahrer):
        neuer = generiere_und_speichere_csrf(request)
        return templates.render_km_eingabe_formular(
            token, csrf_token=neuer,
            hinweis="Bitte einen gültigen Namen eingeben.",
        )

    try:
        kilometerstand = int(kilometerstand_wert)
    except ValueError:
        neuer = generiere_und_speichere_csrf(request)
        return templates.render_km_eingabe_formular(
            token, csrf_token=neuer,
            hinweis="Bitte einen gültigen Kilometerstand eingeben.",
        )

    # security genutzt: Validierung des Kilometerstands
    if not ist_kilometerstand_gueltig(kilometerstand):
        neuer = generiere_und_speichere_csrf(request)
        return templates.render_km_eingabe_formular(
            token, csrf_token=neuer,
            hinweis="Bitte einen plausiblen Kilometerstand eingeben.",
        )

    # security genutzt: Bereinigung des Fahrernamens
    name = reinige_text_einfach(name_fahrer)

    # Foto speichern (falls vorhanden)
    foto_pfad_str = None
    if foto_datei and foto_datei.filename:
        dateiname = f"{token}_{foto_datei.filename}"
        ziel_pfad = UPLOAD_DIR / dateiname
        with ziel_pfad.open("wb") as f:
            f.write(foto_datei.file.read())
        foto_pfad_str = str(ziel_pfad)

    daten = KilometerEingabeRequest(
        name_fahrer=name,
        kilometerstand=kilometerstand,
    )

    erfolg = service.verarbeite_kilometer_eingabe(token, daten, foto_pfad=foto_pfad_str)

    if not erfolg:
        neuer = generiere_und_speichere_csrf(request)
        return templates.render_km_eingabe_formular(
            token, csrf_token=neuer,
            hinweis="Der Link ist ungültig oder wurde bereits verwendet.",
        )

    return templates.render_km_danke_seite()


# ---------------------------------------------------------
# Historie
# ---------------------------------------------------------

@router.get("/fahrzeug/{fahrzeug_id}/historie", response_class=HTMLResponse)
def fahrzeug_historie(request: Request, fahrzeug_id: int):
    """
    Zeigt die Historie der KM-Einträge für ein Fahrzeug an.

    - Überprüft, ob der Benutzer eingeloggt ist.
    - Lädt die KM-Historie für das ausgewählte Fahrzeug.
    """
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung

    fahrzeug = service.hole_fahrzeug_details(fahrzeug_id)
    if not fahrzeug:
        return RedirectResponse(url="/dashboard", status_code=302)

    km_eintraege = service.hole_km_historie(fahrzeug_id)
    return templates.render_km_historie(fahrzeug, km_eintraege)
