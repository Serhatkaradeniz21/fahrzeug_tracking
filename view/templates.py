# view/templates.py
# Dieses Modul enthält Funktionen zur Erstellung von HTML-Templates.
# Es sorgt für ein einheitliches Layout und erleichtert die Darstellung von Fehlern und Inhalten.

from typing import List, Optional, Dict, Any
from model.km_model import FahrzeugAnzeige, KmAnforderungResponse


# ---------------------------------------------------------
# Grundlayout – jede Seite nutzt diese Basisfunktion
# ---------------------------------------------------------

def layout(titel: str, inhalt: str) -> str:
    """
    Diese Funktion erzeugt das Grundlayout für alle HTML-Seiten.
    Sie stellt sicher, dass jede Seite ein konsistentes Design hat und die CSS-Datei eingebunden ist.
    """
    return f"""
    <html>
        <head>
            <title>{titel}</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            {inhalt}
        </body>
    </html>
    """


def fehler(text: Optional[str]) -> str:
    """
    Diese Funktion erzeugt eine standardisierte Fehlerbox, die auf der Seite angezeigt wird.
    Sie wird verwendet, um dem Benutzer Fehlermeldungen oder Hinweise anzuzeigen.
    """
    return f"<p class='hinweis-fehler'>{text}</p>" if text else ""


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------

def render_login_seite(csrf_token: str, fehlermeldung: Optional[str] = None) -> str:
    inhalt = f"""
        <div class="seite-zentriert">
            <h1>FahrzeugTracking – Login</h1>
            {fehler(fehlermeldung)}
            <form method="post" class="formular">
                <input type="hidden" name="csrf_token" value="{csrf_token}" />

                <div class="formular-gruppe">
                    <label>Benutzername:</label>
                    <input type="text" name="benutzername" required />
                </div>

                <div class="formular-gruppe">
                    <label>Passwort:</label>
                    <input type="password" name="passwort" required />
                </div>

                <div class="button-gruppe zentriert">
                    <button type="submit" class="btn-primar">Anmelden</button>
                </div>
            </form>
        </div>
    """
    return layout("Login", inhalt)


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------

def render_dashboard(fahrzeuge: List[FahrzeugAnzeige], csrf_token: str) -> str:
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


# ---------------------------------------------------------
# KM-Eingabe (Fahrer)
# ---------------------------------------------------------

def render_km_eingabe_formular(token: str, csrf_token: str, hinweis: Optional[str] = None) -> str:
    inhalt = f"""
        <div class="seite-zentriert">
            <h1>Kilometerstand eingeben</h1>
            {fehler(hinweis)}

            <form method="post" enctype="multipart/form-data" class="formular"
                  action="/km/eingabe/{token}">

                <input type="hidden" name="csrf_token" value="{csrf_token}" />

                <div class="formular-gruppe">
                    <label>Name:</label>
                    <input type="text" name="name_fahrer" required />
                </div>

                <div class="formular-gruppe">
                    <label>Kilometerstand:</label>
                    <input type="number" min="0" name="kilometerstand_wert" required />
                </div>

                <div class="formular-gruppe">
                    <label>Foto (optional):</label>
                    <input type="file" name="foto_datei" accept="image/*" capture="environment" />
                </div>

                <div class="button-gruppe zentriert">
                    <button class="btn-primar">Senden</button>
                </div>
            </form>
        </div>
    """
    return layout("KM-Eingabe", inhalt)


def render_km_danke_seite() -> str:
    return layout(
        "Danke",
        """
        <div class="seite-zentriert">
            <h1>Danke!</h1>
            <p>Der Kilometerstand wurde gespeichert.</p>
        </div>
        """
    )


# ---------------------------------------------------------
# Fahrzeug neu / bearbeiten
# ---------------------------------------------------------

def render_fahrzeug_neu(csrf_token: str, hinweis: Optional[str] = None) -> str:
    inhalt = f"""
        <div class="seite-zentriert">
            <h1>Neues Fahrzeug anlegen</h1>
            {fehler(hinweis)}

            <form method="post" class="formular">
                <input type="hidden" name="csrf_token" value="{csrf_token}" />

                <div class="formular-gruppe">
                    <label>Kennzeichen:</label>
                    <input type="text" name="kennzeichen" required />
                </div>

                <div class="formular-gruppe">
                    <label>Modell:</label>
                    <input type="text" name="bezeichnung" required />
                </div>

                <div class="formular-gruppe">
                    <label>KM-Stand:</label>
                    <input type="number" min="0" name="aktueller_km_wert" required />
                </div>

                <div class="formular-gruppe">
                    <label>TÜV bis:</label>
                    <input type="date" name="tuev_bis" required />
                </div>

                <div class="formular-gruppe">
                    <label>Nächster Ölwechsel (km):</label>
                    <input type="number" min="0" name="naechster_oelwechsel_km_wert" required />
                </div>

                <div class="button-gruppe zentriert">
                    <button class="btn-primar">Speichern</button>
                    <a href="/dashboard" class="btn-zweit">Abbrechen</a>
                </div>
            </form>
        </div>
    """
    return layout("Fahrzeug anlegen", inhalt)


def render_fahrzeug_bearbeiten(fahrzeug: Dict[str, Any], csrf_token: str, hinweis: Optional[str] = None) -> str:
    tuev = fahrzeug.get("tuev_bis")
    tuev_wert = tuev.strftime("%Y-%m-%d") if tuev else ""

    inhalt = f"""
        <div class="seite-zentriert">
            <h1>Fahrzeug bearbeiten</h1>
            {fehler(hinweis)}

            <form method="post" class="formular">
                <input type="hidden" name="csrf_token" value="{csrf_token}" />

                <div class="formular-grid">

                    <div class="formular-gruppe">
                        <label>Kennzeichen:</label>
                        <input type="text" name="kennzeichen"
                               value="{fahrzeug.get('kennzeichen','')}" required />
                    </div>

                    <div class="formular-gruppe">
                        <label>Modell:</label>
                        <input type="text" name="bezeichnung"
                               value="{fahrzeug.get('bezeichnung','')}" required />
                    </div>

                    <div class="formular-gruppe">
                        <label>KM-Stand:</label>
                        <input type="number" name="aktueller_km_wert"
                               value="{fahrzeug.get('aktueller_km',0)}"
                               min="0" required />
                    </div>

                    <div class="formular-gruppe">
                        <label>TÜV bis:</label>
                        <input type="date" name="tuev_bis"
                               value="{tuev_wert}" required />
                    </div>

                    <div class="formular-gruppe">
                        <label>Nächster Ölwechsel (km):</label>
                        <input type="number" name="naechster_oelwechsel_km_wert"
                               value="{fahrzeug.get('naechster_oelwechsel_km',0)}"
                               min="0" required />
                    </div>

                </div>

                <div class="button-gruppe zentriert">
                    <button class="btn-primar">Speichern</button>
                    <a href="/dashboard" class="btn-zweit">Zurück</a>
                </div>
            </form>
        </div>
    """

    return layout("Fahrzeug bearbeiten", inhalt)


# ---------------------------------------------------------
# KM-Link erzeugt
# ---------------------------------------------------------

def render_km_link_anzeige(antwort: KmAnforderungResponse) -> str:
    inhalt = f"""
        <div class="seite-zentriert">
            <h1>KM-Link erzeugt</h1>

            <p>Fahrzeug-ID: {antwort.fahrzeug_id}</p>

            <div class="link-box">
                <input type="text" id="kmLink" value="{antwort.link_url}" readonly />
                <button onclick="kopiereLink()" class="btn-primar">Kopieren</button>
            </div>

            <p><a href="/dashboard" class="btn-zweit">Zurück zum Dashboard</a></p>
        </div>

        <script>
            function kopiereLink() {{
                var feld = document.getElementById("kmLink");
                feld.select();
                feld.setSelectionRange(0, 99999);
                document.execCommand("copy");
                alert("Link kopiert.");
            }}
        </script>
    """
    return layout("KM-Link", inhalt)


# ---------------------------------------------------------
# KM-Historie
# ---------------------------------------------------------

def render_km_historie(fahrzeug: Dict[str, Any], km_eintraege: List[Dict[str, Any]]) -> str:
    zeilen = ""

    for e in km_eintraege:
        datum = e.get("erfasst_am")
        datum_text = datum.strftime("%d.%m.%Y %H:%M") if datum else "-"

        km = e.get("aktueller_km", "-")
        fahrer = e.get("fahrer_name") or "-"
        token = e.get("token") or "-"

        if e.get("foto_pfad"):
            foto = f'<a target="_blank" href="/{e["foto_pfad"]}">Foto</a>'
        else:
            foto = "-"

        zeilen += f"""
        <tr>
            <td>{datum_text}</td>
            <td>{km}</td>
            <td>{fahrer}</td>
            <td>{token}</td>
            <td>{foto}</td>
        </tr>
        """

    inhalt = f"""
        <div class="seite-zentriert">
            <h1>KM-Historie</h1>
            <h2>{fahrzeug.get('kennzeichen')} – {fahrzeug.get('bezeichnung')}</h2>

            <div class="tabelle-container">
                <table class="daten-tabelle">
                    <thead>
                        <tr>
                            <th>Datum</th>
                            <th>Kilometerstand</th>
                            <th>Fahrer</th>
                            <th>Token</th>
                            <th>Foto</th>
                        </tr>
                    </thead>
                    <tbody>
                        {zeilen}
                    </tbody>
                </table>
            </div>

            <div class="button-gruppe zentriert">
                <a href="/dashboard" class="btn-zweit">Zurück zum Dashboard</a>
            </div>
        </div>
    """

    return layout("KM-Historie", inhalt)
