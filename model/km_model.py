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
    Beinhaltet Stammdaten sowie abgeleitete Informationen:
    - Restzeit bis TÜV
    - Restkilometer bis Ölwechsel
    - letzte KM-Meldung
    - letzte Anforderung / Linkstatus
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
        # Falls das Repository zusätzliche Felder liefert,
        # werden sie nicht strikt validiert.
        # Das macht das System erweiterbar.
        extra = "ignore"


# ---------------------------------------------------------
# Modell: KilometerEingabeRequest
# ---------------------------------------------------------

class KilometerEingabeRequest(BaseModel):
    """
    Daten, die ein Fahrer im KM-Formular eingibt.
    Validierung erfolgt über Pydantic:
    - Name muss mind. 1 Zeichen haben
    - Kilometerwert muss >= 0 sein
    """
    name_fahrer: str = Field(min_length=1)
    kilometerstand: int = Field(ge=0)


# ---------------------------------------------------------
# Modell: KmAnforderungResponse
# ---------------------------------------------------------

class KmAnforderungResponse(BaseModel):
    """
    Antwortmodell für die Erzeugung eines KM-Anforderungslinks.
    Wird im Template angezeigt.
    """
    fahrzeug_id: int
    token: str
    link_url: str
