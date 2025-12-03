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
)

# 👉 NEUE IMPORTS – DIE EINZIG RICHTIGEN
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

router = APIRouter()
service = KilometerService()

# Upload-Verzeichnis
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------
# CSRF-Token Verwaltung
# ---------------------------------------------------------

def generiere_und_speichere_csrf(request: Request) -> str:
    if "csrf_token" not in request.session:
        roher_token = erzeuge_csrf_token()
        signierter = signiere_csrf_token(roher_token)
        request.session["csrf_token"] = signierter
    return request.session["csrf_token"]


def csrf_pruefen(request: Request, empfangener_token: str) -> bool:
    gespeicherter = request.session.get("csrf_token")
    if not gespeicherter:
        return False
    if gespeicherter != empfangener_token:
        return False
    return pruefe_signierten_csrf_token(empfangener_token)


# ---------------------------------------------------------
# Login-Management
# ---------------------------------------------------------

def pruefe_login_erforderlich(request: Request) -> bool:
    return request.session.get("eingeloggt") is True


def login_oder_redirect(request: Request):
    if not pruefe_login_erforderlich(request):
        return RedirectResponse("/login", status_code=302)
    return None


# Login GET
@router.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    csrf = generiere_und_speichere_csrf(request)
    return render_login_seite(csrf_token=csrf)


# Login POST
@router.post("/login", response_class=HTMLResponse)
def login_post(
    request: Request,
    benutzername: str = Form(...),
    passwort: str = Form(...),
    csrf_token: str = Form(...),
):
    if not csrf_pruefen(request, csrf_token):
        neu = generiere_und_speichere_csrf(request)
        return render_login_seite(csrf_token=neu, fehlermeldung="Ungültiger CSRF-Token.")

    if not ist_benutzername_gueltig(benutzername):
        neu = generiere_und_speichere_csrf(request)
        return render_login_seite(csrf_token=neu, fehlermeldung="Benutzername ungültig.")

    name = reinige_text_einfach(benutzername)

    if not pruefe_login(name, passwort):
        neu = generiere_und_speichere_csrf(request)
        return render_login_seite(csrf_token=neu, fehlermeldung="Login fehlgeschlagen.")

    request.session["eingeloggt"] = True
    return RedirectResponse("/dashboard", status_code=302)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung

    fahrzeuge = service.hole_fahrzeuge_fuer_dashboard()
    csrf = generiere_und_speichere_csrf(request)
    return render_dashboard(fahrzeuge, csrf_token=csrf)


# ---------------------------------------------------------
# Fahrzeug anlegen / bearbeiten / löschen
# ---------------------------------------------------------

@router.get("/fahrzeug/neu", response_class=HTMLResponse)
def fahrzeug_neu_get(request: Request):
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung
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
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung

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
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung

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
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung

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
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung

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
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung

    if not csrf_pruefen(request, csrf_token):
        return RedirectResponse("/dashboard", status_code=302)

    antwort = service.erzeuge_km_anforderung(fahrzeug_id)
    return render_km_link_anzeige(antwort)


# ---------------------------------------------------------
# KM-Eingabe Fahrer
# ---------------------------------------------------------

@router.get("/km/eingabe/{token}", response_class=HTMLResponse)
def km_eingabe_formular_anzeigen(request: Request, token: str):
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
    if not csrf_pruefen(request, csrf_token):
        neu = generiere_und_speichere_csrf(request)
        return render_km_eingabe_formular(token, csrf_token=neu, hinweis="Ungültiger CSRF-Token.")

    if not ist_name_gueltig(name_fahrer):
        neu = generiere_und_speichere_csrf(request)
        return render_km_eingabe_formular(token, csrf_token=neu, hinweis="Ungültiger Fahrername.")

    try:
        km = int(kilometerstand_wert)
    except ValueError:
        neu = generiere_und_speichere_csrf(request)
        return render_km_eingabe_formular(token, csrf_token=neu, hinweis="Ungültiger Kilometerstand.")

    if not ist_kilometerstand_gueltig(km):
        neu = generiere_und_speichere_csrf(request)
        return render_km_eingabe_formular(token, csrf_token=neu, hinweis="Plausiblen Kilometerstand eingeben.")

    name = reinige_text_einfach(name_fahrer)

    foto_pfad_str = None
    if foto_datei and foto_datei.filename:
        dateiname = f"{token}_{foto_datei.filename}"
        ziel = UPLOAD_DIR / dateiname
        with ziel.open("wb") as f:
            f.write(foto_datei.file.read())
        foto_pfad_str = str(ziel)

    daten = KilometerEingabeRequest(
        name_fahrer=name,
        kilometerstand=km,
    )

    erfolg = service.verarbeite_kilometer_eingabe(token, daten, foto_pfad=foto_pfad_str)

    if not erfolg:
        neu = generiere_und_speichere_csrf(request)
        return render_km_eingabe_formular(token, csrf_token=neu, hinweis="Link ungültig oder bereits genutzt.")

    return render_km_danke_seite()


# ---------------------------------------------------------
# Historie
# ---------------------------------------------------------

@router.get("/fahrzeug/{fahrzeug_id}/historie", response_class=HTMLResponse)
def fahrzeug_historie(request: Request, fahrzeug_id: int):
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung

    fahrzeug = service.hole_fahrzeug_details(fahrzeug_id)
    if not fahrzeug:
        return RedirectResponse("/dashboard", status_code=302)

    km_eintraege = service.hole_km_historie(fahrzeug_id)
    return render_km_historie(fahrzeug, km_eintraege)
