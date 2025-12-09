"""
# Controller-Schicht für das FahrzeugTracking-System

## Enthaltene Kategorien und Funktionen:

### 1. CSRF-Token-Management
- `generiere_und_speichere_csrf`
- `csrf_pruefen`

### 2. Login- und Logout-Management
- `login_get`
- `login_post`

### 3. Dashboard-Management
- Anzeige aller Fahrzeuge und ihrer aktuellen Zustände.

### 4. Fahrzeugverwaltung
- Routen zum Anlegen, Bearbeiten und Löschen von Fahrzeugen.

### 5. Kilometeranforderungen
- Generierung von Links für die Kilometerstandserfassung.

### 6. Kilometerstandserfassung
- Verarbeitung der Eingaben von Fahrern.

### 7. Historie
- Anzeige der Kilometerstandshistorie eines Fahrzeugs.
"""

"""
Dieses Modul definiert die HTTP-Routen und die zugehörige Logik für Benutzerinteraktionen.
Es verbindet die Service-Schicht mit der Präsentationsschicht und stellt sicher, dass die
richtigen Daten an die Templates übergeben werden.

Hauptfunktionen:
- CSRF-Token-Management
- Login- und Logout-Management
- Dashboard- und Fahrzeugverwaltung
- Kilometeranforderungen und -eingaben
"""

# controller/km_controller.py
# HTTP-Routen und Logik für Benutzerinteraktionen.
# Verbindung zwischen Service- und Präsentationsschicht.

from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse

from service.km_service import KilometerService
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
    ist_disponent_eingeloggt,
)

from view.templates.dashboard_templates import render_dashboard
from view.templates.login_templates import render_login_seite
from view.templates.km_templates import (
    render_km_eingabe_formular,
    render_km_danke_seite,
    render_km_link_anzeige,
    render_km_historie,
)
from view.templates.fahrzeug_templates import (
    render_fahrzeug_neu,
    render_fahrzeug_bearbeiten,
)

# *** GANZ WICHTIG: router MUSS HIER DEFINIERT SEIN ***
router = APIRouter()
service = KilometerService()

# Upload-Verzeichnis
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------
# CSRF-Token Verwaltung
# ---------------------------------------------------------

def generiere_und_speichere_csrf(request: Request) -> str:
    """
    Generiert (bzw. erneuert) einen CSRF-Token, signiert ihn
    und speichert ihn in der Sitzung.

    Wichtig:
    - Wenn noch kein Token existiert ODER der letzte als verbraucht
      markiert wurde, wird ein neuer Token erzeugt und das
      Verbraucht-Flag zurückgesetzt.
    """
    token_verbraucht = request.session.get("csrf_token_verbraucht", False)

    if ("csrf_token" not in request.session) or token_verbraucht:
        roher_token = erzeuge_csrf_token()
        signierter = signiere_csrf_token(roher_token)
        request.session["csrf_token"] = signierter
        request.session["csrf_token_verbraucht"] = False  # neuer Token ist unverbraucht

    return request.session["csrf_token"]



def csrf_pruefen(request: Request, empfangener_token: str) -> bool:
    """
    Überprüft die Gültigkeit eines empfangenen CSRF-Tokens und ob er bereits verwendet wurde.
    """
    gespeicherter = request.session.get("csrf_token")
    token_verbraucht = request.session.get("csrf_token_verbraucht", False)

    if not gespeicherter or token_verbraucht:
        return False

    if gespeicherter != empfangener_token:
        return False

    if not pruefe_signierten_csrf_token(empfangener_token):
        return False

    # Markiere den Token als verbraucht
    request.session["csrf_token_verbraucht"] = True
    return True


# ---------------------------------------------------------
# Login-Management
# ---------------------------------------------------------

def pruefe_login_erforderlich(request: Request) -> bool:
    """
    Überprüft, ob der Benutzer (Disponent) eingeloggt ist.
    Die eigentliche Session-Prüfung erfolgt zentral im Sicherheitsmodul.
    """
    return ist_disponent_eingeloggt(request)


def login_oder_redirect(request: Request):
    """
    Leitet den Benutzer auf die Login-Seite weiter, falls er nicht eingeloggt ist.
    Wird von allen geschützten Routen (z. B. Dashboard, Fahrzeugverwaltung, Historie) aufgerufen.
    """
    if not pruefe_login_erforderlich(request):
        return RedirectResponse("/login", status_code=302)
    return None


@router.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    """
    Zeigt die Login-Seite an und generiert einen neuen CSRF-Token.
    """
    csrf = generiere_und_speichere_csrf(request)
    return render_login_seite(csrf_token=csrf)


@router.post("/login", response_class=HTMLResponse)
def login_post(
    request: Request,
    benutzername: str = Form(...),
    passwort: str = Form(...),
    csrf_token: str = Form(...),
):
    """
    Verarbeitet die Login-Daten des Benutzers.
    """
    if not csrf_pruefen(request, csrf_token):
        neu = generiere_und_speichere_csrf(request)
        request.session["csrf_token_verbraucht"] = False  # Setze neuen Token als unverbraucht
        return render_login_seite(csrf_token=neu, fehlermeldung="Ungültiger oder verbrauchter CSRF-Token.")

    if not ist_benutzername_gueltig(benutzername):
        neu = generiere_und_speichere_csrf(request)
        request.session["csrf_token_verbraucht"] = False
        return render_login_seite(csrf_token=neu, fehlermeldung="Benutzername ungültig.")

    name = reinige_text_einfach(benutzername)

    if not pruefe_login(name, passwort):
        neu = generiere_und_speichere_csrf(request)
        request.session["csrf_token_verbraucht"] = False
        return render_login_seite(csrf_token=neu, fehlermeldung="Login fehlgeschlagen.")

    request.session["eingeloggt"] = True
    return RedirectResponse("/dashboard", status_code=302)


@router.get("/logout")
def logout(request: Request):
    """
    Meldet den Benutzer ab und leitet zur Login-Seite weiter.
    """
    request.session.clear()
    return RedirectResponse("/login", status_code=302)


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    """
    Zeigt das Dashboard mit einer Liste aller Fahrzeuge an.
    Nur für eingeloggte Disponenten zugänglich.
    """
    redirect = login_oder_redirect(request)
    if redirect:
        return redirect

    fahrzeuge = service.hole_fahrzeuge_fuer_dashboard()
    csrf = generiere_und_speichere_csrf(request)
    return render_dashboard(fahrzeuge, csrf_token=csrf)


# ---------------------------------------------------------
# Fahrzeug anlegen / bearbeiten / löschen
# ---------------------------------------------------------

@router.get("/fahrzeug/neu", response_class=HTMLResponse)
def fahrzeug_neu_get(request: Request):
    """
    Zeigt das Formular zum Anlegen eines neuen Fahrzeugs an.
    """
    redirect = login_oder_redirect(request)
    if redirect:
        return redirect
    csrf = generiere_und_speichere_csrf(request)
    return render_fahrzeug_neu(csrf_token=csrf)


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
    """
    redirect = login_oder_redirect(request)
    if redirect:
        return redirect

    if not csrf_pruefen(request, csrf_token):
        return RedirectResponse("/dashboard", status_code=302)

    try:
        km = int(aktueller_km_wert)
        oel = int(naechster_oelwechsel_km_wert)
    except ValueError:
        neu = generiere_und_speichere_csrf(request)
        return render_fahrzeug_neu(csrf_token=neu, hinweis="Nur Zahlen eingeben!")

    service.erstelle_fahrzeug(
        kennzeichen=kennzeichen,
        bezeichnung=bezeichnung,
        aktueller_km=km,
        tuev_bis=tuev_bis,
        naechster_oelwechsel_km=oel,
    )

    return RedirectResponse("/dashboard", status_code=302)


@router.get("/fahrzeug/{fahrzeug_id}/bearbeiten", response_class=HTMLResponse)
def fahrzeug_bearbeiten_get(request: Request, fahrzeug_id: int):
    """
    Zeigt das Formular zum Bearbeiten eines bestehenden Fahrzeugs an.
    """
    redirect = login_oder_redirect(request)
    if redirect:
        return redirect

    fzg = service.hole_fahrzeug_details(fahrzeug_id)
    if not fzg:
        return RedirectResponse("/dashboard", status_code=302)

    csrf = generiere_und_speichere_csrf(request)
    return render_fahrzeug_bearbeiten(fzg, csrf_token=csrf)


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
    """
    redirect = login_oder_redirect(request)
    if redirect:
        return redirect

    if not csrf_pruefen(request, csrf_token):
        return RedirectResponse("/dashboard", status_code=302)

    try:
        km = int(aktueller_km_wert)
        oel = int(naechster_oelwechsel_km_wert)
    except ValueError:
        fzg = service.hole_fahrzeug_details(fahrzeug_id)
        neu = generiere_und_speichere_csrf(request)
        return render_fahrzeug_bearbeiten(fzg, csrf_token=neu, hinweis="Nur Zahlen eingeben!")

    service.aktualisiere_fahrzeug(
        fahrzeug_id=fahrzeug_id,
        kennzeichen=kennzeichen,
        bezeichnung=bezeichnung,
        aktueller_km=km,
        tuev_bis=tuev_bis,
        naechster_oelwechsel_km=oel,
    )

    return RedirectResponse("/dashboard", status_code=302)


@router.post("/fahrzeug/{fahrzeug_id}/loeschen")
def fahrzeug_loeschen_post(
    request: Request,
    fahrzeug_id: int,
    csrf_token: str = Form(...),
):
    """
    Löscht ein Fahrzeug aus der Datenbank.
    """
    redirect = login_oder_redirect(request)
    if redirect:
        return redirect

    if not csrf_pruefen(request, csrf_token):
        return RedirectResponse("/dashboard", status_code=302)

    service.loesche_fahrzeug(fahrzeug_id)
    return RedirectResponse("/dashboard", status_code=302)


# ---------------------------------------------------------
# KM-Link anfordern
# ---------------------------------------------------------

@router.post("/km/anforderung/{fahrzeug_id}", response_class=HTMLResponse)
def km_anforderung_erzeugen(
    request: Request,
    fahrzeug_id: int,
    csrf_token: str = Form(...),
):
    """
    Fordert einen neuen Kilometer-Link für ein Fahrzeug an.
    """
    redirect = login_oder_redirect(request)
    if redirect:
        return redirect

    if not csrf_pruefen(request, csrf_token):
        return RedirectResponse("/dashboard", status_code=302)

    antwort = service.erzeuge_km_anforderung(fahrzeug_id)
    return render_km_link_anzeige(antwort)


# ---------------------------------------------------------
# KM-Eingabe Fahrer
# ---------------------------------------------------------

@router.get("/km/eingabe/{token}", response_class=HTMLResponse)
def km_eingabe_formular_anzeigen(request: Request, token: str):
    """
    Zeigt das Formular zur Eingabe der Kilometerstände durch den Fahrer an.
    """
    csrf = generiere_und_speichere_csrf(request)
    return render_km_eingabe_formular(token, csrf_token=csrf)


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
    Verarbeitet die Eingaben des Fahrers für die Kilometerstandserfassung.
    """

    # 1. CSRF prüfen
    if not csrf_pruefen(request, csrf_token):
        neu = generiere_und_speichere_csrf(request)
        return render_km_eingabe_formular(token, csrf_token=neu, hinweis="Ungültiger CSRF-Token.")

    # 2. Fahrername prüfen
    if not ist_name_gueltig(name_fahrer):
        neu = generiere_und_speichere_csrf(request)
        return render_km_eingabe_formular(token, csrf_token=neu, hinweis="Ungültiger Fahrername.")

    # 3. Kilometerstand in int umwandeln
    try:
        km = int(kilometerstand_wert)
    except ValueError:
        neu = generiere_und_speichere_csrf(request)
        return render_km_eingabe_formular(token, csrf_token=neu, hinweis="Ungültiger Kilometerstand (keine Zahl).")

    # 4. Bereichsprüfung (nur grob, z.B. 0–2.000.000)
    if not ist_kilometerstand_gueltig(km):
        neu = generiere_und_speichere_csrf(request)
        return render_km_eingabe_formular(token, csrf_token=neu, hinweis="Plausiblen Kilometerstand eingeben.")

    # 5. Name bereinigen
    name = reinige_text_einfach(name_fahrer)

    # 6. Foto speichern (optional)
    if foto_datei and foto_datei.filename:
        ziel = UPLOAD_DIR / f"{token}_{foto_datei.filename}"
        ziel.write_bytes(foto_datei.file.read())
        foto_pfad_str = str(ziel)
    else:
        foto_pfad_str = None

    # 7. Datenobjekt für Service bauen
    daten = KilometerEingabeRequest(
        name_fahrer=name,
        kilometerstand=km,
    )

    # 8. Service aufrufen
    status = service.verarbeite_kilometer_eingabe(token, daten, foto_pfad=foto_pfad_str)

    if status == "ok":
        # HIER: Danke-Seite ohne Dashboard-Button (Template anpassen)
        return render_km_danke_seite()

    neu = generiere_und_speichere_csrf(request)

    if status == "token_ungueltig":
        hinweis = "Der Link ist ungültig oder wurde bereits verwendet."
    elif status == "fahrzeug_fehlt":
        hinweis = "Das zugehörige Fahrzeug existiert nicht mehr."
    elif status == "km_zu_niedrig":
        hinweis = "Der eingegebene Kilometerstand darf nicht kleiner als der aktuelle Stand des Fahrzeugs sein."
    else:
        hinweis = "Die Kilometer-Eingabe konnte nicht verarbeitet werden."

    return render_km_eingabe_formular(token, csrf_token=neu, hinweis=hinweis)


# ---------------------------------------------------------
# Historie
# ---------------------------------------------------------

@router.get("/fahrzeug/{fahrzeug_id}/historie", response_class=HTMLResponse)
def fahrzeug_historie(request: Request, fahrzeug_id: int):
    """
    Zeigt die Historie der Kilometerstände für ein Fahrzeug an.
    Nur für eingeloggte Disponenten zugänglich.
    """
    redirect = login_oder_redirect(request)
    if redirect:
        return redirect

    fahrzeug = service.hole_fahrzeug_details(fahrzeug_id)
    if not fahrzeug:
        return RedirectResponse("/dashboard", status_code=302)

    km_eintraege = service.hole_km_historie(fahrzeug_id)
    return render_km_historie(fahrzeug, km_eintraege)
