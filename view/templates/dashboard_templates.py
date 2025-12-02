# dashboard_templates.py
# Funktionen zur Erstellung des Dashboards.
#
# Ziel:
# - Dynamische Generierung der Fahrzeugübersicht.
# - Einbindung von CSRF-Schutz in Formularen.
#
# Enthaltene Funktionen:
# - render_dashboard: Erstellt die HTML-Seite für das Dashboard.

from typing import List
from .base_templates import layout
from model.km_model import FahrzeugAnzeige

def render_dashboard(fahrzeuge: List[FahrzeugAnzeige], csrf_token: str) -> str:
    """
    Erstellt die HTML-Seite für das Dashboard mit der Übersicht der Fahrzeuge.
    """
    zeilen = ""

    for f in fahrzeuge:
        tuev_text = f.tuev_bis.strftime("%d.%m.%Y") if f.tuev_bis else "-"
        tuev_rest = f"{f.tuev_rest_tage} Tage" if f.tuev_rest_tage is not None else "-"

        oel_rest = (
            f"{f.rest_km_bis_oelwechsel} km" if f.rest_km_bis_oelwechsel is not None else "-"
        )
        oel_naechst = f"{f.naechster_oelwechsel_km} km" if f.naechster_oelwechsel_km else "-"

        letzter_fahrer = f.letzter_fahrer_name or "-"
        letzter_km_datum = (
            f.letzter_km_datum.strftime("%d.%m.%Y %H:%M") if f.letzter_km_datum else "-"
        )

        letzter_link = (
            f.letzter_link_versandt_am.strftime("%d.%m.%Y %H:%M")
            if f.letzter_link_versandt_am else "-"
        )

        status = "Offen" if f.link_noch_offen else "Erledigt"

        # Dynamische Zeilen für die Fahrzeugübersichtstabelle
        zeilen += f"""
        <tr>
            <td>{f.id}</td>
            <td>{f.kennzeichen}</td>
            <td>{f.bezeichnung}</td>
            <td>{f.aktueller_km} km</td>
            <td>{tuev_text}</td>
            <td>{tuev_rest}</td>
            <td>{oel_naechst}</td>
            <td>{oel_rest}</td>
            <td>{letzter_fahrer}</td>
            <td>{letzter_km_datum}</td>
            <td>{letzter_link}</td>
            <td>{status}</td>

            <td>
                <form method="post" action="/km/anforderung/{f.id}">
                    <input type="hidden" name="csrf_token" value="{csrf_token}" />
                    <button class="btn-klein">KM-Link</button>
                </form>
            </td>

            <td>
                <a href="/fahrzeug/{f.id}/historie" class="btn-klein">Historie</a>
            </td>

            <td>
                <a href="/fahrzeug/{f.id}/bearbeiten" class="btn-klein">Bearbeiten</a>
            </td>

            <td>
                <form method="post"
                      action="/fahrzeug/{f.id}/loeschen"
                      onsubmit="return confirm('Fahrzeug wirklich löschen?');">
                    <input type="hidden" name="csrf_token" value="{csrf_token}" />
                    <button class="btn-klein btn-gefahr">Löschen</button>
                </form>
            </td>
        </tr>
        """

    # HTML-Inhalt für das Dashboard zusammenstellen
    inhalt = f"""
        <div class="kopfzeile">
            <h1>Fahrzeug-Dashboard</h1>
            <div class="kopf-buttons">
                <a href="/fahrzeug/neu" class="btn-primar">Neues Fahrzeug</a>
                <a href="/logout" class="btn-zweit">Logout</a>
            </div>
        </div>

        <div class="tabelle-container">
            <table class="daten-tabelle">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Kennzeichen</th>
                        <th>Bezeichnung</th>
                        <th>KM aktuell</th>
                        <th>TÜV bis</th>
                        <th>TÜV Rest</th>
                        <th>Nächster Ölwechsel</th>
                        <th>Rest bis Ölwechsel</th>
                        <th>Letzter Fahrer</th>
                        <th>Letzte KM-Meldung</th>
                        <th>Letzter Link</th>
                        <th>Status</th>
                        <th>KM-Link</th>
                        <th>Historie</th>
                        <th>Bearbeiten</th>
                        <th>Löschen</th>
                    </tr>
                </thead>
                <tbody>{zeilen}</tbody>
            </table>
        </div>
    """

    return layout("Dashboard", inhalt)