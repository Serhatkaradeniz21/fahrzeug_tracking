# datenbank/repository.py
# Dieses Modul dient als Schnittstelle zwischen der Anwendung und der Datenbank.
# Ziel ist es, alle SQL-Abfragen zu kapseln und die Datenbankzugriffe sicher und effizient zu gestalten.

from typing import Any, Dict, List, Optional
from mysql.connector import Error


class KilometerRepository:
    def __init__(self, verbindung) -> None:
        # Initialisiert die Verbindung zur Datenbank
        self.verbindung = verbindung

    # ---------------------------------------------------------
    # Fahrzeuge
    # ---------------------------------------------------------

    def hole_alle_fahrzeuge(self) -> List[Dict[str, Any]]:
        """
        Ruft alle Fahrzeuge aus der Datenbank ab.

        - Gibt eine Liste von Dictionaries zurück, die die wichtigsten Fahrzeugdaten enthalten.
        - Jedes Dictionary enthält Felder wie Kennzeichen, Modell und Kilometerstand.
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
        Gibt ein Dictionary mit den Fahrzeugdaten zurück oder None, falls nicht gefunden.
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

        - `fahrzeug_id`: Die ID des Fahrzeugs, das aktualisiert werden soll.
        - Aktualisiert Felder wie Kennzeichen, Modell, Kilometerstand, TÜV-Datum und Ölwechsel.
        - Führt die Änderungen in einer Transaktion aus.
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

        - Entfernt auch zugehörige Kilometer-Einträge und Anforderungen.
        - `fahrzeug_id`: Die ID des Fahrzeugs, das gelöscht werden soll.
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
        Speichert einen KM-Eintrag und aktualisiert den KM-Stand des Fahrzeugs.
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
        Liefert die letzten KM-Einträge für ein Fahrzeug.
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
        Liefert den letzten KM-Eintrag eines Fahrzeugs.
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
        Legt eine neue KM-Anforderung mit Token an.
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
        Holt eine KM-Anforderung anhand eines Tokens.
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
        Holt die letzte KM-Anforderung eines Fahrzeugs.
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
        Markiert eine Kilometeranforderung als verbraucht.
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
