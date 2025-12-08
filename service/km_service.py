"""
# Service-Schicht für das FahrzeugTracking-System

## Enthaltene Kategorien und Funktionen:

### 1. Dashboard / Fahrzeugliste
- `hole_fahrzeuge_fuer_dashboard`

### 2. Fahrzeugverwaltung
- `hole_fahrzeug_details`
- `erstelle_fahrzeug`
- `aktualisiere_fahrzeug`
- `loesche_fahrzeug`

### 3. KM-Anforderungen / Links
- `erzeuge_km_anforderung`

### 4. KM-Eingabe / Historie
- `verarbeite_kilometer_eingabe`
- `hole_km_historie`

### 5. Wartungslogik
- `_pruefe_wartungen_und_benachrichtigen`

### 6. Hilfsfunktionen
- `wert_oder_none`

### 7. Mailversand
- `_sende_warnmail`
"""

# service/km_service.py
# Geschäftslogik für das FahrzeugTracking-System.
# Ziel:
# - Verbindung zwischen Controller-Schicht und Datenbank.
# - Konsistente Verarbeitung der Daten.
from typing import Optional, List, Dict, Any
from datetime import date
import os
import smtplib
import secrets

from model.km_model import (
    FahrzeugAnzeige,
    KmAnforderungResponse,
    KilometerEingabeRequest,
)
from datenbank.repository import KilometerRepository
from datenbank.verbindung import get_db_verbindung


# ---------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------

def wert_oder_none(eintrag: dict, feld: str) -> Optional[Any]:
    """
    Hilfsfunktion, um sicher Werte aus einem Dictionary abzurufen.

    - Gibt den Wert des Feldes zurück oder None, falls das Feld nicht existiert.
    """
    return eintrag.get(feld) if eintrag else None


# ---------------------------------------------------------
# Geschäftslogik
# ---------------------------------------------------------

class KilometerService:
    def __init__(self) -> None:
        # Verbindung zur Datenbank aufbauen
        verbindung = get_db_verbindung()
        self.repo = KilometerRepository(verbindung)

    # ---------------------------------------------------------
    # Dashboard / Fahrzeugliste
    # ---------------------------------------------------------

    def hole_fahrzeuge_fuer_dashboard(self) -> List[FahrzeugAnzeige]:
        """
        Holt alle Fahrzeuge und ergänzt sie um Anzeige-Infos wie TÜV-Resttage,
        Ölwechsel-Infos und Link-Status.
        """
        roh_daten = self.repo.hole_alle_fahrzeuge()
        fahrzeuge: List[FahrzeugAnzeige] = []

        heute = date.today()

        for datensatz in roh_daten:
            fahrzeug_id = datensatz["id"]

            # Letzter KM-Eintrag (für Fahrername + Datum)
            letzter = self.repo.hole_letzten_km_eintrag_fuer_fahrzeug(fahrzeug_id)
            datensatz["letzter_fahrer_name"] = wert_oder_none(letzter, "fahrer_name")
            datensatz["letzter_km_datum"] = wert_oder_none(letzter, "erfasst_am")

            # TÜV-Resttage berechnen
            tuev_bis = datensatz.get("tuev_bis")
            if tuev_bis:
                datensatz["tuev_rest_tage"] = (tuev_bis - heute).days
            else:
                datensatz["tuev_rest_tage"] = None

            # Rest-Kilometer bis zum nächsten Ölwechsel berechnen
            naechster_oel_km = datensatz.get("naechster_oelwechsel_km")
            aktueller_km = datensatz.get("aktueller_km") or 0
            if naechster_oel_km is not None:
                datensatz["rest_km_bis_oelwechsel"] = naechster_oel_km - aktueller_km
            else:
                datensatz["rest_km_bis_oelwechsel"] = None

            # Link-Status für die letzte Kilometeranforderung prüfen
            letzte_anforderung = self.repo.hole_letzte_km_anforderung_fuer_fahrzeug(
                fahrzeug_id
            )
            if letzte_anforderung:
                datensatz["letzter_link_versandt_am"] = letzte_anforderung.get(
                    "erstellt_am"
                )
                datensatz["link_noch_offen"] = not bool(
                    letzte_anforderung.get("verbraucht")
                )
            else:
                datensatz["letzter_link_versandt_am"] = None
                datensatz["link_noch_offen"] = False

            fahrzeuge.append(FahrzeugAnzeige(**datensatz))

        return fahrzeuge

    # ---------------------------------------------------------
    # Fahrzeuge verwalten
    # ---------------------------------------------------------

    def hole_fahrzeug_details(self, fahrzeug_id: int) -> Optional[Dict[str, Any]]:
        """
        Ruft die Basisdaten eines Fahrzeugs aus der Datenbank ab.
        """
        return self.repo.hole_fahrzeug_nach_id(fahrzeug_id)

    def erstelle_fahrzeug(
        self,
        kennzeichen: str,
        bezeichnung: str,
        aktueller_km: int,
        tuev_bis,
        naechster_oelwechsel_km: int,
    ) -> None:
        """
        Legt ein neues Fahrzeug in der Datenbank an.
        """
        self.repo.fuege_fahrzeug_hinzu(
            kennzeichen=kennzeichen,
            bezeichnung=bezeichnung,
            aktueller_km=aktueller_km,
            tuev_bis=tuev_bis,
            naechster_oelwechsel_km=naechster_oelwechsel_km,
        )

    def aktualisiere_fahrzeug(
        self,
        fahrzeug_id: int,
        kennzeichen: str,
        bezeichnung: str,
        aktueller_km: int,
        tuev_bis,
        naechster_oelwechsel_km: int,
    ) -> None:
        """
        Aktualisiert die Daten eines vorhandenen Fahrzeugs und stößt danach
        die Wartungsprüfung an.
        """
        self.repo.aktualisiere_fahrzeug(
            fahrzeug_id=fahrzeug_id,
            kennzeichen=kennzeichen,
            bezeichnung=bezeichnung,
            aktueller_km=aktueller_km,
            tuev_bis=tuev_bis,
            naechster_oelwechsel_km=naechster_oelwechsel_km,
        )

        fahrzeug_nach_update = self.repo.hole_fahrzeug_nach_id(fahrzeug_id)
        print("WARTUNGSPRUEFUNG STARTET")
        print("Fahrzeugdaten:", fahrzeug_nach_update)

        if fahrzeug_nach_update:
            self._pruefe_wartungen_und_benachrichtigen(fahrzeug_nach_update)

    def loesche_fahrzeug(self, fahrzeug_id: int) -> None:
        """
        Entfernt ein Fahrzeug aus der Datenbank.
        """
        self.repo.loesche_fahrzeug(fahrzeug_id)

    # ---------------------------------------------------------
    # KM-Anforderungen / Links
    # ---------------------------------------------------------

    def erzeuge_km_anforderung(self, fahrzeug_id: int) -> KmAnforderungResponse:
        """
        Erzeugt eine Kilometeranforderung mit Token und Link.
        """
        token = secrets.token_urlsafe(32)
        link_url = f"http://127.0.0.1:8000/km/eingabe/{token}"

        self.repo.speichere_km_anforderung(fahrzeug_id, token)

        return KmAnforderungResponse(
            fahrzeug_id=fahrzeug_id,
            token=token,
            link_url=link_url,
        )

    # ---------------------------------------------------------
    # KM-Eingabe / Historie + Wartungsprüfung
    # ---------------------------------------------------------

    def verarbeite_kilometer_eingabe(
        self,
        token: str,
        daten: KilometerEingabeRequest,
        foto_pfad: Optional[str] = None,
    ) -> str:
        """
        Verarbeitet eine Kilometer-Eingabe basierend auf einem Token.

        Rückgabewert (Status-String):
        - "ok"                -> alles gut, gespeichert
        - "token_ungueltig"   -> Token existiert nicht (oder wird nicht gefunden)
        - "fahrzeug_fehlt"    -> Fahrzeug existiert nicht (mehr)

        Die KM-Plausibilitätsprüfung (neuer KM < aktueller KM) gibt nur eine Warnung
        in der Konsole aus, blockiert aber nicht den Speichervorgang.
        """
        print("DEBUG: verarbeite_kilometer_eingabe gestartet")
        print("DEBUG: Token:", token)
        print("DEBUG: Daten:", daten)

        km_anforderung = self.repo.hole_km_anforderung_per_token(token)
        print("DEBUG: km_anforderung:", km_anforderung)

        if not km_anforderung:
            print("DEBUG: Keine KM-Anforderung gefunden – Token ungültig oder nicht in DB.")
            return "token_ungueltig"

        fahrzeug_id = km_anforderung["fahrzeug_id"]

        fahrzeug = self.repo.hole_fahrzeug_nach_id(fahrzeug_id)
        print("DEBUG: fahrzeug:", fahrzeug)
        if not fahrzeug:
            print("DEBUG: Kein Fahrzeug zur fahrzeug_id gefunden.")
            return "fahrzeug_fehlt"

        aktueller_km = fahrzeug.get("aktueller_km", 0) or 0
        print("DEBUG: aktueller_km:", aktueller_km)
        print("DEBUG: eingegebener_km:", daten.kilometerstand)

        # Nur Warnung, keine Blockade
        if daten.kilometerstand < aktueller_km:
            print(
                f"Warnung: KM-Eingabe ({daten.kilometerstand}) liegt unter aktuellem KM "
                f"({aktueller_km}). Eintrag wird trotzdem verarbeitet."
            )

        # KM-Eintrag speichern (inkl. Foto, falls vorhanden)
        self.repo.speichere_km_eintrag(
            fahrzeug_id=fahrzeug_id,
            fahrer_name=daten.name_fahrer,
            neuer_km=daten.kilometerstand,
            token=token,
            foto_pfad=foto_pfad,
        )

        # Link als verbraucht markieren, damit er nur einmal nutzbar ist
        if "id" in km_anforderung:
            self.repo.markiere_km_anforderung_verbraucht(km_anforderung["id"])

        # Aktuelle Fahrzeugdaten holen (inkl. neuem KM-Stand)
        fahrzeug = self.repo.hole_fahrzeug_nach_id(fahrzeug_id)
        if fahrzeug:
            self._pruefe_wartungen_und_benachrichtigen(fahrzeug)

        print("DEBUG: KM-Eingabe erfolgreich verarbeitet.")
        return "ok"

    def hole_km_historie(self, fahrzeug_id: int) -> List[Dict[str, Any]]:
        """
        Liefert die KM-Historie für ein Fahrzeug.

        Wird vom Controller in /fahrzeug/{fahrzeug_id}/historie aufgerufen.
        """
        return self.repo.hole_km_eintraege_fuer_fahrzeug(fahrzeug_id)

    # ---------------------------------------------------------
    # Wartungslogik (TÜV + Ölwechsel)
    # ---------------------------------------------------------

    def _pruefe_wartungen_und_benachrichtigen(self, fahrzeug: Dict[str, Any]) -> None:
        """
        Prüft TÜV- und Ölwechsel-Schwellen und verschickt bei Bedarf Warnmails.
        Wird nach jeder neuen Kilometer-Eingabe oder manuellen Aktualisierung aufgerufen.
        """
        empfaenger = os.getenv("DISPONENT_EMAIL", "karadeniz.serhat21@gmail.com")

        fahrzeug_text = f"{fahrzeug.get('kennzeichen', '')} - {fahrzeug.get('bezeichnung', '')}"

        # TÜV prüfen (Hinweis 3 Monate vorher)
        tuev_bis = fahrzeug.get("tuev_bis")
        if tuev_bis:
            heute = date.today()
            diff_tage = (tuev_bis - heute).days
            if 0 <= diff_tage <= 90:
                betreff = f"TÜV-Hinweis für Fahrzeug {fahrzeug_text}"
                text = (
                    f"Für das Fahrzeug {fahrzeug_text} läuft der TÜV am {tuev_bis.strftime('%d.%m.%Y')} ab.\n"
                    f"Restlaufzeit: {diff_tage} Tage.\n"
                    "Bitte rechtzeitig einen Termin für die Hauptuntersuchung planen."
                )
                self._sende_warnmail(empfaenger, betreff, text)

        # Ölwechsel prüfen (Intervall 15.000 km, Warnungen bei 10k / 13k / 15k)
        aktueller_km = fahrzeug.get("aktueller_km") or 0
        naechster_oel_km = fahrzeug.get("naechster_oelwechsel_km")

        if naechster_oel_km is not None and naechster_oel_km > 0:
            basis_letzter_oelwechsel = naechster_oel_km - 15000
            km_seit_letztem_oel = aktueller_km - basis_letzter_oelwechsel

            warnstufen = [
                (10000, 13000, "10.000 km seit letztem Ölwechsel"),
                (13000, 15000, "13.000 km seit letztem Ölwechsel"),
                (15000, float("inf"), "15.000 km erreicht – Ölwechsel fällig"),
            ]

            warnstufe = None
            for untergrenze, obergrenze, text_warnung in warnstufen:
                if untergrenze <= km_seit_letztem_oel < obergrenze:
                    warnstufe = text_warnung
                    break

            if warnstufe is not None:
                betreff = f"Ölwechsel-Hinweis für Fahrzeug {fahrzeug_text}"
                text = (
                    f"Für das Fahrzeug {fahrzeug_text} wurden ca. {km_seit_letztem_oel} km "
                    f"seit dem letzten Ölwechsel gefahren.\n"
                    f"Aktueller Kilometerstand: {aktueller_km} km.\n"
                    f"Hinweis: {warnstufe}.\n"
                    "Bitte einen Ölwechsel einplanen."
                )
                self._sende_warnmail(empfaenger, betreff, text)

    # ---------------------------------------------------------
    # Mailversand (Prototyp, z.B. mit MailHog, UTF-8)
    # ---------------------------------------------------------

    def _sende_warnmail(self, empfaenger: str, betreff: str, text: str) -> None:
        """
        Versendet eine Warnmail.

        - Verwendet UTF-8, damit Umlaute wie Ü/Ö/Ä korrekt übertragen werden.
        - Im Prototyp wird über localhost:1025 gesendet (z.B. MailHog).
        - Bei Fehlern wird nur eine Meldung in der Konsole ausgegeben.
        """
        from email.mime.text import MIMEText
        from email.header import Header
        from email.utils import formataddr

        absender = os.getenv("MAIL_ABSENDER", "karadeniz.serhat21@gmail.com")

        msg = MIMEText(text, _charset="utf-8")
        msg["Subject"] = Header(betreff, "utf-8")
        msg["From"] = formataddr(("FahrzeugTracking", absender))
        msg["To"] = empfaenger

        try:
            with smtplib.SMTP("localhost", 1025) as server:
                server.sendmail(absender, [empfaenger], msg.as_string())
            print(f"Warnmail versendet an {empfaenger}: {betreff}")
        except Exception as fehler:
            print("Warnmail konnte nicht gesendet werden:", fehler)
            print("Geplante Mail:", betreff)
            print(text)
