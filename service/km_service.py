"""
Die Datei `km_service.py` wurde in der vierten Entwicklungsphase erstellt und implementiert die
Service-Schicht des FahrzeugTracking-Systems. Sie umfasst:

1. Geschäftslogik für das Dashboard:
   - Berechnung von Restkilometern, TÜV-Resttagen und Link-Status.

2. Fahrzeugverwaltung:
   - Methoden zum Anlegen, Bearbeiten und Löschen von Fahrzeugen.

3. Kilometeranforderungen:
   - Generierung von Token und Links für die Kilometerstandserfassung.

4. Kilometerstandserfassung:
   - Validierung und Speicherung von Kilometerständen.

5. Wartungslogik:
   - Prüfung von TÜV- und Ölwechsel-Schwellen und Versand von Warnmails.
"""

# service/km_service.py
# Geschäftslogik für das FahrzeugTracking-System.
#
# Ziel:
# - Verbindung zwischen Controller-Schicht und Datenbank.
# - Konsistente Verarbeitung der Daten.
#
# Enthaltene Kategorien und Funktionen:
# 1. Dashboard / Fahrzeugliste:
#    - hole_fahrzeuge_fuer_dashboard
# 2. Fahrzeugverwaltung:
#    - hole_fahrzeug_details
#    - erstelle_fahrzeug
#    - aktualisiere_fahrzeug
#    - loesche_fahrzeug
# 3. KM-Anforderungen / Links:
#    - erzeuge_km_anforderung
# 4. KM-Eingabe / Historie:
#    - verarbeite_kilometer_eingabe
#    - hole_km_historie
# 5. Wartungslogik:
#    - _pruefe_wartungen_und_benachrichtigen
# 6. Hilfsfunktionen:
#    - wert_oder_none
# 7. Mailversand:
#    - _sende_warnmail

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
    - Wird häufig verwendet, um Fehler bei fehlenden Schlüsseln zu vermeiden.
    """
    return eintrag.get(feld) if eintrag else None

# ---------------------------------------------------------
# Geschäftslogik
# ---------------------------------------------------------

class KilometerService:
    """
    Service-Klasse für die Geschäftslogik des FahrzeugTracking-Systems.

    Diese Klasse stellt Methoden bereit, um Daten zwischen der Controller-Schicht
    und der Datenbank zu verarbeiten. Sie enthält Logik für das Dashboard,
    Fahrzeugverwaltung, Kilometeranforderungen und Wartungsprüfungen.

    Attribute:
        repo: Eine Instanz des KilometerRepository für den Datenbankzugriff.
    """

    def __init__(self) -> None:
        """
        Initialisiert den KilometerService und stellt die Verbindung zur Datenbank her.
        """
        verbindung = get_db_verbindung()
        self.repo = KilometerRepository(verbindung)

    # ---------------------------------------------------------
    # Dashboard / Fahrzeugliste
    # ---------------------------------------------------------

    def hole_fahrzeuge_fuer_dashboard(self) -> List[FahrzeugAnzeige]:
        """
        Holt alle Fahrzeuge und berechnet zusätzliche Anzeige-Informationen.

        Returns:
            Eine Liste von FahrzeugAnzeige-Objekten mit berechneten Feldern wie
            TÜV-Resttage, Restkilometer bis zum Ölwechsel und Link-Status.
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

            # TüV-Resttage berechnen
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

            # Fahrzeugdaten in die Liste aufnehmen
            fahrzeuge.append(FahrzeugAnzeige(**datensatz))

        return fahrzeuge

    # ---------------------------------------------------------
    # Fahrzeuge verwalten
    # ---------------------------------------------------------

    def hole_fahrzeug_details(self, fahrzeug_id: int) -> Optional[Dict[str, Any]]:
        """
        Ruft die Basisdaten eines Fahrzeugs aus der Datenbank ab.

        Args:
            fahrzeug_id: Die eindeutige ID des Fahrzeugs.

        Returns:
            Ein Dictionary mit den Fahrzeugdaten oder None, falls kein Fahrzeug gefunden wurde.
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

        Args:
            kennzeichen: Das Kennzeichen des Fahrzeugs.
            bezeichnung: Die Modellbezeichnung des Fahrzeugs.
            aktueller_km: Der aktuelle Kilometerstand des Fahrzeugs.
            tuev_bis: Das Datum, bis zu dem der TÜV gültig ist.
            naechster_oelwechsel_km: Die Kilometerzahl für den nächsten Ölwechsel.
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
        Aktualisiert die Daten eines vorhandenen Fahrzeugs.

        Args:
            fahrzeug_id: Die ID des Fahrzeugs, das aktualisiert werden soll.
            kennzeichen: Das neue Kennzeichen des Fahrzeugs.
            bezeichnung: Die neue Modellbezeichnung des Fahrzeugs.
            aktueller_km: Der aktualisierte Kilometerstand des Fahrzeugs.
            tuev_bis: Das neue TÜV-Datum.
            naechster_oelwechsel_km: Die neue Kilometerzahl für den nächsten Ölwechsel.
        """
        # Daten in der Datenbank aktualisieren
        self.repo.aktualisiere_fahrzeug(
            fahrzeug_id=fahrzeug_id,
            kennzeichen=kennzeichen,
            bezeichnung=bezeichnung,
            aktueller_km=aktueller_km,
            tuev_bis=tuev_bis,
            naechster_oelwechsel_km=naechster_oelwechsel_km,
        )

        # Aktualisierte Fahrzeugdaten holen
        fahrzeug_nach_update = self.repo.hole_fahrzeug_nach_id(fahrzeug_id)
        print("WARTUNGSPRUEFUNG STARTET")
        print("Fahrzeugdaten:", fahrzeug_nach_update)

        if fahrzeug_nach_update:
            # Wartungslogik auf Basis der aktuellen Daten anstoßen
            self._pruefe_wartungen_und_benachrichtigen(fahrzeug_nach_update)

    def loesche_fahrzeug(self, fahrzeug_id: int) -> None:
        """
        Entfernt ein Fahrzeug aus der Datenbank.

        Args:
            fahrzeug_id: Die ID des Fahrzeugs, das gelöscht werden soll.
        """
        self.repo.loesche_fahrzeug(fahrzeug_id)

    # ---------------------------------------------------------
    # KM-Anforderungen / Links
    # ---------------------------------------------------------

    def erzeuge_km_anforderung(self, fahrzeug_id: int) -> KmAnforderungResponse:
        """
        Erzeugt eine Kilometeranforderung mit Token und Link.

        Args:
            fahrzeug_id: Die ID des Fahrzeugs, für das die Anforderung erstellt wird.

        Returns:
            Ein KmAnforderungResponse-Objekt mit den Details der Anforderung.
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
    ) -> bool:
        """
        Verarbeitet eine Kilometer-Eingabe basierend auf einem Token.

        Args:
            token: Der Token, der die Eingabe authentifiziert.
            daten: Ein KilometerEingabeRequest-Objekt mit den Eingabedaten.
            foto_pfad: Der Pfad zum Foto des Kilometerstands (optional).

        Returns:
            True, wenn die Eingabe erfolgreich verarbeitet wurde, andernfalls False.
        """
        km_anforderung = self.repo.hole_km_anforderung_per_token(token)
        if not km_anforderung:
            return False

        fahrzeug_id = km_anforderung["fahrzeug_id"]

        
        fahrzeug = self.repo.hole_fahrzeug_nach_id(fahrzeug_id)
        if not fahrzeug:
            return False

        aktueller_km = fahrzeug.get("aktueller_km", 0)

        #KM-PRÜFUNG
        if daten.kilometerstand < aktueller_km:
            print("KM-Eingabe zu niedrig – wird abgelehnt.")
            return False

        #KM-Eintrag speichern (inkl. Foto, falls vorhanden)
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

        return True
        

    def hole_km_historie(self, fahrzeug_id: int) -> List[Dict[str, Any]]:
        """
        Liefert die Kilometer-Historie für ein Fahrzeug.

        Args:
            fahrzeug_id: Die ID des Fahrzeugs.

        Returns:
            Eine Liste von Dictionaries mit den Kilometer-Einträgen.
        """
        return self.repo.hole_km_eintraege_fuer_fahrzeug(fahrzeug_id)

    # ---------------------------------------------------------
    # Wartungslogik (TÜV + Ölwechsel)
    # ---------------------------------------------------------

    def _pruefe_wartungen_und_benachrichtigen(self, fahrzeug: Dict[str, Any]) -> None:
        """
        Prüft TÜV- und Ölwechsel-Schwellen und verschickt bei Bedarf Warnmails.

        Args:
            fahrzeug: Ein Dictionary mit den Fahrzeugdaten.
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
            # Letzter Ölwechsel = naechster_oelwechsel_km - 15.000
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
    # Mailversand (Prototyp, z.B. mit MailHog)
    # ---------------------------------------------------------

    def _sende_warnmail(self, empfaenger: str, betreff: str, text: str) -> None:
        """
        Versendet eine Warnmail.

        Args:
            empfaenger: Die E-Mail-Adresse des Empfängers.
            betreff: Der Betreff der E-Mail.
            text: Der Inhalt der E-Mail.
        """
        absender = os.getenv("MAIL_ABSENDER", "karadeniz.serhat21@gmail.com")

        nachricht = f"Subject: {betreff}\nTo: {empfaenger}\nFrom: {absender}\n\n{text}"
        try:
            with smtplib.SMTP("localhost", 1025) as server:
                server.sendmail(absender, [empfaenger], nachricht)
            print(f"Warnmail versendet an {empfaenger}: {betreff}")
        except Exception as fehler:
            print("Warnmail konnte nicht gesendet werden:", fehler)
            print("Geplante Mail:", betreff)
            print(text)
