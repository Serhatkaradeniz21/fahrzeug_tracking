"""
Die Datei `km_model.py` wurde in der sechsten Entwicklungsphase erstellt und definiert die
Datenmodelle des FahrzeugTracking-Systems. Sie umfasst:

1. FahrzeugAnzeige:
   - Repräsentiert ein Fahrzeug im Dashboard mit berechneten Feldern wie TÜV-Resttage.

2. KilometerEingabeRequest:
   - Beschreibt die Eingaben eines Fahrers für die Kilometerstandserfassung.

3. KmAnforderungResponse:
   - Antwortmodell für die Generierung eines Kilometeranforderungslinks.
"""

# model/km_model.py
# Pydantic-Modelle für das FahrzeugTracking-System.
#
# Ziel:
# - Beschreibung der Datenstrukturen für Controller, Service, Repository und Templates.
#
# Enthaltene Modelle:
# - FahrzeugAnzeige: Repräsentiert ein Fahrzeug im Dashboard.
# - KilometerEingabeRequest: Beschreibt die Eingabe eines Kilometerstands.

from pydantic import BaseModel, Field 
from typing import Optional
from datetime import date, datetime


# ---------------------------------------------------------
# Modell: FahrzeugAnzeige
# ---------------------------------------------------------

class FahrzeugAnzeige(BaseModel):
    """
    Repräsentiert ein Fahrzeug im Dashboard.

    Attribute:
        id (int): Die eindeutige ID des Fahrzeugs.
        kennzeichen (str): Das Kennzeichen des Fahrzeugs.
        bezeichnung (str): Die Modellbezeichnung des Fahrzeugs.
        aktueller_km (int): Der aktuelle Kilometerstand (muss >= 0 sein).
        tuev_bis (Optional[date]): Das Datum, bis zu dem der TÜV gültig ist.
        tuev_rest_tage (Optional[int]): Die verbleibenden Tage bis zum TÜV.
        naechster_oelwechsel_km (Optional[int]): Die Kilometerzahl für den nächsten Ölwechsel.
        rest_km_bis_oelwechsel (Optional[int]): Die verbleibenden Kilometer bis zum nächsten Ölwechsel.
        letzter_fahrer_name (Optional[str]): Der Name des letzten Fahrers.
        letzter_km_datum (Optional[datetime]): Das Datum der letzten Kilometer-Meldung.
        letzter_link_versandt_am (Optional[datetime]): Das Datum, an dem der letzte Link versandt wurde.
        link_noch_offen (bool): Gibt an, ob der letzte Link noch gültig ist.
    """
    id: int
    kennzeichen: str
    bezeichnung: str
    aktueller_km: int = Field(ge=0)# Aktueller Kilometerstand

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
        # unbekannte Felder werden ignoriert falls enthalten schlägt nicht fehl und stürtzt ab.
        extra = "ignore"


# ---------------------------------------------------------
# Modell: KilometerEingabeRequest
# ---------------------------------------------------------

class KilometerEingabeRequest(BaseModel):
    """
    Daten, die ein Fahrer im Kilometer-Formular eingibt.

    Attribute:
        name_fahrer (str): Der Name des Fahrers (mindestens 1 Zeichen).
        kilometerstand (int): Der eingegebene Kilometerstand (muss >= 0 sein).
    """
    name_fahrer: str = Field(min_length=1)
    kilometerstand: int = Field(ge=0)


# ---------------------------------------------------------
# Modell: KmAnforderungResponse
# ---------------------------------------------------------

class KmAnforderungResponse(BaseModel):
    """
    Antwortmodell für die Erzeugung eines Kilometer-Anforderungslinks.

    Attribute:
        fahrzeug_id (int): Die ID des Fahrzeugs, für das der Link erstellt wurde.
        token (str): Ein eindeutiger Token, der den Link sichert.
        link_url (str): Die URL, die der Fahrer aufrufen kann, um Kilometer einzugeben.
    """
    fahrzeug_id: int
    token: str
    link_url: str
