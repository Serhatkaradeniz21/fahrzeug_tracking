# model/km_model.py
# Pydantic-Modelle für das FahrzeugTracking-System.
# Diese Modelle beschreiben die Datenstrukturen, die zwischen
# Controller, Service, Repository und Template übertragen werden.

from pydantic import BaseModel, Field 
from typing import Optional
from datetime import date, datetime


# ---------------------------------------------------------
# Modell: FahrzeugAnzeige
# ---------------------------------------------------------

class FahrzeugAnzeige(BaseModel):
    """
    Repräsentiert ein Fahrzeug im Dashboard.

    - Enthält Stammdaten wie Kennzeichen und Bezeichnung.
    - Berechnete Felder wie Restzeit bis TÜV oder Restkilometer bis Ölwechsel.
    - Historische Daten wie der letzte Fahrername und das Datum der letzten Kilometer-Meldung.
    """
    id: int
    kennzeichen: str
    bezeichnung: str
    aktueller_km: int = Field(ge=0)

    # TÜV
    tuev_bis: Optional[date] = None
    tuev_rest_tage: Optional[int] = None

    # Ölwechsel
    naechster_oelwechsel_km: Optional[int] = None
    rest_km_bis_oelwechsel: Optional[int] = None

    # Historie / letzter KM-Eintrag
    letzter_fahrer_name: Optional[str] = None
    letzter_km_datum: Optional[datetime] = None

    # Link-/Anforderungsstatus
    letzter_link_versandt_am: Optional[datetime] = None
    link_noch_offen: bool = False

    class Config:
        # Zusätzliche Felder werden ignoriert, um Erweiterbarkeit zu ermöglichen.
        extra = "ignore"


# ---------------------------------------------------------
# Modell: KilometerEingabeRequest
# ---------------------------------------------------------

class KilometerEingabeRequest(BaseModel):
    """
    Daten, die ein Fahrer im Kilometer-Formular eingibt.

    Wichtige Punkte:
    - `name_fahrer`: Der Name des Fahrers, muss mindestens 1 Zeichen lang sein.
    - `kilometerstand`: Der eingegebene Kilometerstand, muss größer oder gleich 0 sein.
    """
    name_fahrer: str = Field(min_length=1)
    kilometerstand: int = Field(ge=0)


# ---------------------------------------------------------
# Modell: KmAnforderungResponse
# ---------------------------------------------------------

class KmAnforderungResponse(BaseModel):
    """
    Antwortmodell für die Erzeugung eines Kilometer-Anforderungslinks.

    Wichtige Punkte:
    - `fahrzeug_id`: Die ID des Fahrzeugs, für das der Link erstellt wurde.
    - `token`: Ein eindeutiger Token, der den Link sichert.
    - `link_url`: Die URL, die der Fahrer aufrufen kann, um Kilometer einzugeben.
    """
    fahrzeug_id: int
    token: str
    link_url: str
