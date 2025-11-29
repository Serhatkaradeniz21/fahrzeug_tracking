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
└── hauptprogramm.py  # Einstiegspunkt der Anwendung
```

## Installation
1. **Repository klonen:**
   ```bash
   git clone https://github.com/Serhatkaradeniz21/fahrzeug_tracking.git
   ```
2. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Datenbank einrichten:**
   - MySQL-Server starten
   - SQL-Skripte im Ordner `sql/` ausführen
4. **Anwendung starten:**
   ```bash
   uvicorn hauptprogramm:app --reload
   ```

## Nutzung
- Öffnen Sie die Anwendung im Browser unter `http://127.0.0.1:8000`.
- Melden Sie sich mit den Standardzugangsdaten an (siehe `.env`-Datei).
- Verwalten Sie Fahrzeuge, Kilometeranforderungen und Einträge über das Dashboard.


---
Vielen Dank, dass Sie dieses Projekt verwenden! Bei Fragen oder Problemen können Sie gerne ein Issue im Repository erstellen.