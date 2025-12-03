# datenbank/repository.py
# Schnittstelle zwischen Anwendung und Datenbank.
#
# Ziel:
# - Kapselung aller SQL-Abfragen.
# - Sicherer und effizienter Datenbankzugriff.
#
# Enthaltene Funktionen:
# - hole_alle_fahrzeuge: Ruft alle Fahrzeuge ab.
# - hole_fahrzeug_nach_id: Ruft ein Fahrzeug anhand der ID ab.
# - fuege_fahrzeug_hinzu: Fügt ein neues Fahrzeug hinzu.
# - aktualisiere_fahrzeug: Aktualisiert die Stammdaten eines Fahrzeugs.
# - loesche_fahrzeug: Löscht ein Fahrzeug aus der Datenbank.
# - speichere_km_eintrag: Speichert einen KM-Eintrag für ein Fahrzeug.
# - hole_km_eintraege_fuer_fahrzeug: Ruft KM-Einträge für ein Fahrzeug ab.
# - hole_letzten_km_eintrag_fuer_fahrzeug: Ruft den letzten KM-Eintrag für ein Fahrzeug ab.
# - speichere_km_anforderung: Legt eine neue KM-Anforderung an.
# - hole_km_anforderung_per_token: Holt eine KM-Anforderung anhand eines Tokens.
# - hole_letzte_km_anforderung_fuer_fahrzeug: Holt die letzte KM-Anforderung eines Fahrzeugs.
# - markiere_km_anforderung_verbraucht: Markiert eine Kilometeranforderung als verbraucht.

from typing import Any, Dict, List, Optional
from mysql.connector import Error


class KilometerRepository:
    """
    Repository-Klasse für den Zugriff auf die Kilometer-Datenbank.

    Diese Klasse kapselt alle Datenbankoperationen, die mit Fahrzeugen, Kilometer-Einträgen
    und Kilometer-Anforderungen zusammenhängen. Sie stellt Methoden bereit, um Daten
    sicher und effizient zu lesen, zu schreiben und zu aktualisieren.

    Attribute:
        verbindung: Die Verbindung zur Datenbank.
    """

    def __init__(self, verbindung) -> None:
        """
        Initialisiert die Verbindung zur Datenbank.

        Args:
            verbindung: Eine aktive Verbindung zur Datenbank.
        """
        self.verbindung = verbindung

    # ---------------------------------------------------------
    # Fahrzeuge
    # ---------------------------------------------------------

    def hole_alle_fahrzeuge(self) -> List[Dict[str, Any]]:
        """
        Ruft alle Fahrzeuge aus der Datenbank ab.

        Returns:
            Eine Liste von Dictionaries, die die wichtigsten Fahrzeugdaten enthalten.
            Jedes Dictionary enthält Felder wie Kennzeichen, Modell und Kilometerstand.
        """
        cursor = self.verbindung.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    id,
                    kennzeichen,
                    modell AS bezeichnung,
                    aktueller_km,
                    tuev_bis,
                    naechster_oelwechsel_km
                FROM fahrzeuge
                """
            )
            return cursor.fetchall()
        except Error as fehler:
            print("Fehler beim Lesen der Fahrzeuge:", fehler)
            return []
        finally:
            cursor.close()

    def hole_fahrzeug_nach_id(
        self, fahrzeug_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Sucht ein Fahrzeug in der Datenbank anhand seiner ID.

        Args:
            fahrzeug_id: Die eindeutige ID des Fahrzeugs.

        Returns:
            Ein Dictionary mit den Fahrzeugdaten oder None, falls kein Fahrzeug gefunden wurde.
        """
        cursor = self.verbindung.cursor(dictionary=True) #dictionary=True für bessere Lesbarkeit

        try:
            cursor.execute(
                """
                SELECT
                    id,
                    kennzeichen,
                    modell AS bezeichnung,
                    aktueller_km,
                    tuev_bis,
                    naechster_oelwechsel_km
                FROM fahrzeuge
                WHERE id = %s
                """,
                (fahrzeug_id,),
            )
            return cursor.fetchone() 
        except Error as fehler:
            print("Fehler beim Lesen eines Fahrzeugs:", fehler)
            return None
        finally:
            cursor.close()

    def fuege_fahrzeug_hinzu(
        self,
        kennzeichen: str,
        bezeichnung: str,
        aktueller_km: int,
        tuev_bis,
        naechster_oelwechsel_km: Optional[int],
    ) -> None:
        """
        Fügt ein neues Fahrzeug in die Datenbank ein.

        Args:
            kennzeichen: Das Kennzeichen des Fahrzeugs.
            bezeichnung: Die Modellbezeichnung des Fahrzeugs.
            aktueller_km: Der aktuelle Kilometerstand des Fahrzeugs.
            tuev_bis: Das Datum, bis zu dem der TÜV gültig ist.
            naechster_oelwechsel_km: Die Kilometerzahl für den nächsten Ölwechsel (optional).
        """
        cursor = self.verbindung.cursor()

        try:
            sql = """
                INSERT INTO fahrzeuge
                    (kennzeichen, modell, aktueller_km, tuev_bis, naechster_oelwechsel_km)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(
                sql,
                (kennzeichen, bezeichnung, aktueller_km, tuev_bis, naechster_oelwechsel_km),
            )
        except Error as fehler:
            print("Fehler beim Anlegen eines Fahrzeugs:", fehler)
        finally:
            cursor.close()

    def aktualisiere_fahrzeug(
        self,
        fahrzeug_id: int,
        kennzeichen: str,
        bezeichnung: str,
        aktueller_km: int,
        tuev_bis,
        naechster_oelwechsel_km: Optional[int],
    ) -> None:
        """
        Aktualisiert die Stammdaten eines Fahrzeugs in der Datenbank.

        Args:
            fahrzeug_id: Die ID des Fahrzeugs, das aktualisiert werden soll.
            kennzeichen: Das neue Kennzeichen des Fahrzeugs.
            bezeichnung: Die neue Modellbezeichnung des Fahrzeugs.
            aktueller_km: Der aktualisierte Kilometerstand des Fahrzeugs.
            tuev_bis: Das neue TÜV-Datum.
            naechster_oelwechsel_km: Die neue Kilometerzahl für den nächsten Ölwechsel (optional).
        """
        cursor = self.verbindung.cursor()

        try:
            sql = """
                UPDATE fahrzeuge
                SET
                    kennzeichen = %s,
                    modell = %s,
                    aktueller_km = %s,
                    tuev_bis = %s,
                    naechster_oelwechsel_km = %s
                WHERE id = %s
            """
            cursor.execute(
                sql,
                (kennzeichen, bezeichnung, aktueller_km, tuev_bis, naechster_oelwechsel_km, fahrzeug_id),
            )
        except Error as fehler:
            print("Fehler beim Aktualisieren eines Fahrzeugs:", fehler)
        finally:
            cursor.close()

    def loesche_fahrzeug(self, fahrzeug_id: int) -> None:
        """
        Löscht ein Fahrzeug aus der Datenbank.

        Args:
            fahrzeug_id: Die ID des Fahrzeugs, das gelöscht werden soll.
        """
        cursor = self.verbindung.cursor()

        try:
            # KM-Einträge löschen
            try:
                cursor.execute(
                    "DELETE FROM km_eintraege WHERE fahrzeug_id = %s",
                    (fahrzeug_id,),
                )
            except Error as fehler:
                print("Hinweis: km_eintraege konnten nicht gelöscht werden:", fehler)

            # KM-Anforderungen löschen
            try:
                cursor.execute(
                    "DELETE FROM km_anforderungen WHERE fahrzeug_id = %s",
                    (fahrzeug_id,),
                )
            except Error as fehler:
                print("Hinweis: km_anforderungen konnten nicht gelöscht werden:", fehler)

            # Fahrzeug löschen
            cursor.execute(
                "DELETE FROM fahrzeuge WHERE id = %s",
                (fahrzeug_id,),
            )
        except Error as fehler:
            print("Fehler beim Löschen eines Fahrzeugs:", fehler)
        finally:
            cursor.close()

    # ---------------------------------------------------------
    # KM-Einträge
    # ---------------------------------------------------------

    def speichere_km_eintrag(
        self,
        fahrzeug_id: int,
        fahrer_name: str,
        neuer_km: int,
        token: str,
        foto_pfad: Optional[str] = None,
    ) -> None:
        """
        Speichert einen Kilometer-Eintrag und aktualisiert den Kilometerstand des Fahrzeugs.

        Args:
            fahrzeug_id: Die ID des Fahrzeugs, für das der Eintrag erstellt wird.
            fahrer_name: Der Name des Fahrers.
            neuer_km: Der neue Kilometerstand.
            token: Der Token, der die Eingabe authentifiziert.
            foto_pfad: Der Pfad zum Foto des Kilometerstands (optional).
        """
        cursor = self.verbindung.cursor()

        try:
            sql_eintrag = """
                INSERT INTO km_eintraege
                    (fahrzeug_id, aktueller_km, fahrer_name, token, foto_pfad)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(
                sql_eintrag,
                (fahrzeug_id, neuer_km, fahrer_name, token, foto_pfad),
            )

            sql_update = """
                UPDATE fahrzeuge
                SET aktueller_km = %s
                WHERE id = %s
            """
            cursor.execute(sql_update, (neuer_km, fahrzeug_id))
        except Error as fehler:
            print("Fehler beim Speichern des Kilometer-Eintrags:", fehler)
        finally:
            cursor.close()

    def hole_km_eintraege_fuer_fahrzeug(
        self, fahrzeug_id: int, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Liefert die letzten Kilometer-Einträge für ein Fahrzeug.

        Args:
            fahrzeug_id: Die ID des Fahrzeugs.
            limit: Die maximale Anzahl der zurückzugebenden Einträge (Standard: 50).

        Returns:
            Eine Liste von Dictionaries mit den Kilometer-Einträgen.
        """
        cursor = self.verbindung.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    id,
                    fahrzeug_id,
                    aktueller_km,
                    fahrer_name,
                    token,
                    foto_pfad,
                    erfasst_am
                FROM km_eintraege
                WHERE fahrzeug_id = %s
                ORDER BY erfasst_am DESC
                LIMIT %s
                """,
                (fahrzeug_id, limit),
            )
            return cursor.fetchall()
        except Error as fehler:
            print("Fehler beim Lesen der KM-Einträge:", fehler)
            return []
        finally:
            cursor.close()

    def hole_letzten_km_eintrag_fuer_fahrzeug(
        self, fahrzeug_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Liefert den letzten Kilometer-Eintrag eines Fahrzeugs.

        Args:
            fahrzeug_id: Die ID des Fahrzeugs.

        Returns:
            Ein Dictionary mit den Daten des letzten Kilometer-Eintrags oder None, falls kein Eintrag vorhanden ist.
        """
        cursor = self.verbindung.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT fahrer_name, aktueller_km, erfasst_am
                FROM km_eintraege
                WHERE fahrzeug_id = %s
                ORDER BY erfasst_am DESC
                LIMIT 1
                """,
                (fahrzeug_id,),
            )
            return cursor.fetchone()
        except Error as fehler:
            print("Fehler beim Lesen des letzten KM-Eintrags:", fehler)
            return None
        finally:
            cursor.close()

    # ---------------------------------------------------------
    # KM-Anforderungen (Token)
    # ---------------------------------------------------------

    def speichere_km_anforderung(self, fahrzeug_id: int, token: str) -> None:
        """
        Legt eine neue Kilometer-Anforderung mit Token an.

        Args:
            fahrzeug_id: Die ID des Fahrzeugs, für das die Anforderung erstellt wird.
            token: Der Token, der die Anforderung identifiziert.
        """
        cursor = self.verbindung.cursor()

        try:
            sql = """
                INSERT INTO km_anforderungen (fahrzeug_id, token)
                VALUES (%s, %s)
            """
            cursor.execute(sql, (fahrzeug_id, token))
        except Error as fehler:
            print("Fehler beim Speichern der KM-Anforderung:", fehler)
        finally:
            cursor.close()

    def hole_km_anforderung_per_token(
        self, token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Holt eine Kilometer-Anforderung anhand eines Tokens.

        Args:
            token: Der Token, der die Anforderung identifiziert.

        Returns:
            Ein Dictionary mit den Daten der Anforderung oder None, falls keine Anforderung gefunden wurde.
        """
        cursor = self.verbindung.cursor(dictionary=True)

        try:
            sql = """
                SELECT 
                    id,
                    fahrzeug_id,
                    token,
                    angeforderter_km,
                    timestamp AS erstellt_am,
                    verbraucht
                FROM km_anforderungen
                WHERE token = %s
            """
            cursor.execute(sql, (token,))
            return cursor.fetchone()
        except Error as fehler:
            print("Fehler beim Lesen der KM-Anforderung:", fehler)
            return None
        finally:
            cursor.close()

    def hole_letzte_km_anforderung_fuer_fahrzeug(
        self, fahrzeug_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Holt die letzte Kilometer-Anforderung eines Fahrzeugs.

        Args:
            fahrzeug_id: Die ID des Fahrzeugs.

        Returns:
            Ein Dictionary mit den Daten der letzten Anforderung oder None, falls keine Anforderung vorhanden ist.
        """
        cursor = self.verbindung.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    id,
                    fahrzeug_id,
                    token,
                    timestamp AS erstellt_am,
                    verbraucht
                FROM km_anforderungen
                WHERE fahrzeug_id = %s
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (fahrzeug_id,),
            )
            return cursor.fetchone()
        except Error as fehler:
            print("Fehler beim Lesen der letzten KM-Anforderung:", fehler)
            return None
        finally:
            cursor.close()

    def markiere_km_anforderung_verbraucht(self, anforderung_id: int) -> None:
        """
        Markiert eine Kilometer-Anforderung als verbraucht.

        Args:
            anforderung_id: Die ID der Anforderung, die als verbraucht markiert werden soll.
        """
        cursor = self.verbindung.cursor()

        try:
            sql = """
                UPDATE km_anforderungen
                SET verbraucht = 1
                WHERE id = %s
            """
            cursor.execute(sql, (anforderung_id,))
        except Error as fehler:
            print("Fehler beim Aktualisieren der KM-Anforderung:", fehler)
        finally:
            cursor.close()
