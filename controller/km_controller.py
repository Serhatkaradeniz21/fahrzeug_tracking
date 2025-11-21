# controller/km_controller.py
# Dieses Modul steuert die HTTP-Routen und die zugehörige Logik für die Benutzerinteraktion.
# Es verbindet die Service-Schicht mit der Präsentationsschicht und stellt sicher,
# dass die richtigen Daten an die Templates übergeben werden.

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
# Hilfsfunktionen 
# ---------------------------------------------------------

def generiere_und_speichere_csrf(request: Request) -> str:
    """
    Erzeugt einen CSRF-Token, signiert ihn
    und speichert ihn in der Session.
    """
    roher_token = erzeuge_csrf_token()
    signierter_token = signiere_csrf_token(roher_token)
    request.session["csrf_token"] = signierter_token
    return signierter_token


def csrf_pruefen(request: Request, empfangener_token: str) -> bool:
    """
    Prüft, ob der empfangene CSRF-Token gültig ist.
    """
    gespeicherter_token = request.session.get("csrf_token")

    if not gespeicherter_token:
        return False

    if gespeicherter_token != empfangener_token:
        return False

    return pruefe_signierten_csrf_token(empfangener_token)


def pruefe_login_erforderlich(request: Request) -> bool:
    """
    Prüft, ob der Disponent eingeloggt ist.
    """
    return request.session.get("eingeloggt") is True


def login_oder_redirect(request: Request):
    """
    Kleine Hilfsfunktion: wenn nicht eingeloggt → Redirect
    """
    if not pruefe_login_erforderlich(request):
        return RedirectResponse(url="/login", status_code=302)
    return None


# ---------------------------------------------------------
# Login / Logout
# ---------------------------------------------------------

@router.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    csrf_token = generiere_und_speichere_csrf(request)
    return templates.render_login_seite(csrf_token=csrf_token)


@router.post("/login", response_class=HTMLResponse)
def login_post(
    request: Request,
    benutzername: str = Form(...),
    passwort: str = Form(...),
    csrf_token: str = Form(...),
):
    if not csrf_pruefen(request, csrf_token):
        csrf_neu = generiere_und_speichere_csrf(request)
        return templates.render_login_seite(
            csrf_token=csrf_neu,
            fehlermeldung="Sicherheitsfehler: CSRF ungültig.",
        )

    if not ist_benutzername_gueltig(benutzername):
        neuer = generiere_und_speichere_csrf(request)
        return templates.render_login_seite(
            csrf_token=neuer,
            fehlermeldung="Benutzername ungültig.",
        )

    benutzer = reinige_text_einfach(benutzername)
    if not pruefe_login(benutzer, passwort):
        neuer = generiere_und_speichere_csrf(request)
        return templates.render_login_seite(
            csrf_token=neuer,
            fehlermeldung="Login fehlgeschlagen.",
        )

    request.session["eingeloggt"] = True
    return RedirectResponse(url="/dashboard", status_code=302)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung

    fahrzeuge = service.hole_fahrzeuge_fuer_dashboard()
    csrf_token = generiere_und_speichere_csrf(request)
    return templates.render_dashboard(fahrzeuge, csrf_token=csrf_token)


# ---------------------------------------------------------
# Fahrzeug anlegen / bearbeiten / löschen
# ---------------------------------------------------------

@router.get("/fahrzeug/neu", response_class=HTMLResponse)
def fahrzeug_neu_get(request: Request):
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
    if not csrf_pruefen(request, csrf_token):
        neuer = generiere_und_speichere_csrf(request)
        return templates.render_km_eingabe_formular(
            token, csrf_token=neuer,
            hinweis="Sicherheitsfehler: Kilometer kleiner als aktuellen Kilometerstand.",
        )

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

    if not ist_kilometerstand_gueltig(kilometerstand):
        neuer = generiere_und_speichere_csrf(request)
        return templates.render_km_eingabe_formular(
            token, csrf_token=neuer,
            hinweis="Bitte einen plausiblen Kilometerstand eingeben.",
        )

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
    fehlermeldung = login_oder_redirect(request)
    if fehlermeldung:
        return fehlermeldung

    fahrzeug = service.hole_fahrzeug_details(fahrzeug_id)
    if not fahrzeug:
        return RedirectResponse(url="/dashboard", status_code=302)

    km_eintraege = service.hole_km_historie(fahrzeug_id)
    return templates.render_km_historie(fahrzeug, km_eintraege)
