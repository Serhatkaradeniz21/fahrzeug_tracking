# Fahrzeug Tracking System

## Projektbeschreibung
Das Fahrzeug Tracking System ist eine Anwendung, die entwickelt wurde, um die Verwaltung von Fahrzeugen, Kilometerständen und zugehörigen Anforderungen zu erleichtern. Es bietet eine benutzerfreundliche Oberfläche und eine robuste Backend-Logik, um die Daten sicher und effizient zu verarbeiten.

## Hauptfunktionen
- **Fahrzeugverwaltung:** Übersicht über alle Fahrzeuge, einschließlich Kennzeichen, Modell und Kilometerstand.
- **Kilometeranforderungen:** Erstellung und Verwaltung von Einmal-Links für Kilometerstandseingaben.
- **Kilometerhistorie:** Anzeige der letzten Kilometer-Einträge für jedes Fahrzeug.
- **Sicherheitsfunktionen:** CSRF-Schutz, Passwort-Hashing und Eingabevalidierung.

## Verwendete Technologien
- **Backend:** Python mit FastAPI
- **Datenbank:** MySQL
- **Frontend:** HTML mit CSS für die Benutzeroberfläche
- **Weitere Tools:** bcrypt für Passwort-Hashing, dotenv für Umgebungsvariablen

## Projektstruktur
```
projekt-fahrzeugtracking/
├── controller/       # Steuert die Routen und die Benutzerinteraktion
├── datenbank/        # Datenbankzugriffe und Repository-Logik
├── dokumentation/    # Projektbezogene Dokumente und Diagramme
├── model/            # Datenmodelle für die Anwendung
├── service/          # Geschäftslogik des Systems
├── sql/              # SQL-Skripte für die Datenbank
├── static/           # Statische Dateien wie CSS und Bilder
├── view/             # HTML-Templates für die Benutzeroberfläche
├── hauptprogramm.py  # Einstiegspunkt der Anwendung
├── start.bat         # Windows Startskript (einfacher Start)
├── requirements.txt  # Python-Abhängigkeiten
└── .env.example      # Vorlage für Konfiguration
```

## Schnellstart (Windows)

### Voraussetzungen
- Python 3.8 oder höher installiert
- MySQL-Server installiert und läuft
- Git (optional, für Klonen)

### Installation

1. **Projekt herunterladen:**
   - Entweder: `git clone https://github.com/Serhatkaradeniz21/fahrzeug_tracking.git`
   - Oder: ZIP-Datei herunterladen und entpacken

2. **Konfiguration einrichten:**
   ```bash
   # Kopieren Sie die Vorlage und erstellen Sie Ihre eigene Konfiguration
   copy .env.example .env
   ```
   - Öffnen Sie `.env` in einem Texteditor
   - Passen Sie die Datenbank-Zugangsdaten an
   - Ändern Sie den SECRET_KEY (beliebiger langer Text)
   - Passen Sie Disponent-Zugangsdaten an

3. **Datenbank einrichten:**
   - Starten Sie MySQL-Server
   - Erstellen Sie eine neue Datenbank namens `fahrzeug_tracking`
   - Führen Sie die SQL-Skripte im Ordner `sql/` aus:
     - `tabellen erstellen.sql`
     - `datenbank unr rechte anlegen.sql`

4. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Anwendung starten:**
   - **Einfach:** Doppelklick auf `start.bat`
   - **Oder manuell:** `uvicorn hauptprogramm:app --reload`

6. **Anwendung nutzen:**
   - Öffnen Sie im Browser: `http://127.0.0.1:8000`
   - Melden Sie sich mit den Zugangsdaten aus `.env` an

## Manuelles Starten (Linux/Mac)

```bash
# 1. Konfiguration erstellen
cp .env.example .env

# 2. .env anpassen (Datenbank, SECRET_KEY, etc.)

# 3. Datenbank einrichten
mysql -u root -p < sql/tabellen erstellen.sql

# 4. Abhängigkeiten installieren
pip install -r requirements.txt

# 5. Server starten
uvicorn hauptprogramm:app --reload
```

## Nutzung
- **Dashboard:** Übersicht aller Fahrzeuge mit TÜV- und Ölwechsel-Infos
- **Fahrzeuge anlegen:** Neues Fahrzeug über Dashboard hinzufügen
- **KM-Link anfordern:** Generiert einen Einmal-Link für Fahrer zur KM-Eingabe
- **Historie:** Kilometerhistorie pro Fahrzeug einsehen

## Standardzugangsdaten
Die Standardzugangsdaten sind in der `.env`-Datei konfiguriert:
- Benutzername: `disponent` (oder wie in .env konfiguriert)
- Passwort: `Dispo123!` (oder wie in .env konfiguriert)

**WICHTIG:** Ändern Sie diese Passwörter vor der ersten Nutzung in der `.env`-Datei!

## Fehlersuche

### Server startet nicht
- Prüfen Sie ob Python installiert ist: `python --version`
- Prüfen Sie ob alle Abhängigkeiten installiert sind: `pip list`
- Prüfen Sie ob die `.env`-Datei existiert

### Datenbankverbindung fehlgeschlagen
- Prüfen Sie ob MySQL läuft
- Prüfen Sie die Zugangsdaten in `.env`
- Prüfen Sie ob die Datenbank `fahrzeug_tracking` existiert

### Port 8000 bereits belegt
- Ändern Sie den Port im Startbefehl: `uvicorn hauptprogramm:app --reload --port 8001`

## Sicherheit
- Ändern Sie den SECRET_KEY in der `.env`-Datei
- Ändern Sie das Disponent-Passwort
- Verwenden Sie starke Passwörter für die Datenbank
- In Produktionsumgebungen: HTTPS verwenden, Firewall konfigurieren

---
Vielen Dank, dass Sie dieses Projekt verwenden! Bei Fragen oder Problemen können Sie gerne ein Issue im Repository erstellen.