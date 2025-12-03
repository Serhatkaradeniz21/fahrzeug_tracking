# view/templates/km_templates.py
# Alle Templates rund um Kilometer-Anforderung, Eingabe und Historie

from typing import List, Any
from .base_templates import layout


def render_km_eingabe_formular(token: str, csrf_token: str, hinweis: str = "") -> str:
    """
    Formular für die KM-Eingabe durch den Fahrer.

    Passt zu:
    - Route:  GET /km/eingabe/{token}
    - Route: POST /km/eingabe/{token}
    - Parameter in km_controller: name_fahrer, kilometerstand_wert, foto_datei, csrf_token
    """
    inhalt = f"""
        <div class="seite-zentriert">
            <h1><a href="/km/eingabe/{token}">Kilometerstand melden</a></h1>

            <p class="hinweis">{hinweis}</p>

            <form method="post" enctype="multipart/form-data" class="formular">
                <input type="hidden" name="csrf_token" value="{csrf_token}" />

                <div class="formular-gruppe">
                    <label>Fahrername:</label>
                    <input type="text" name="name_fahrer" required />
                </div>

                <div class="formular-gruppe">
                    <label>Kilometerstand:</label>
                    <input type="number" name="kilometerstand_wert"
                           required min="0" max="2000000" />
                </div>

                <div class="formular-gruppe">
                    <label>Foto vom Kilometerstand (optional):</label>
                    <input type="file" name="foto_datei" accept="image/*" />
                </div>

                <div class="button-gruppe zentriert">
                    <button type="submit" class="btn-primar">Senden</button>
                </div>
            </form>
        </div>
    """
    return layout("KM-Eingabe", inhalt)


def render_km_danke_seite() -> str:
    """
    Danke-Seite nach erfolgreicher KM-Eingabe.
    Wird aufgerufen in km_controller nach erfolgreichem verarbeite_kilometer_eingabe().
    """
    inhalt = """
        <div class="seite-zentriert">
            <h1>Kilometerstand übermittelt</h1>
            <p>Vielen Dank! Die Daten wurden erfolgreich gespeichert.</p>

            <div class="button-gruppe zentriert">
                <a href="/dashboard" class="btn-primar">Zurück zum Dashboard</a>
            </div>
        </div>
    """
    return layout("KM-Erfassung abgeschlossen", inhalt)


def render_km_link_anzeige(antwort: Any) -> str:
    """
    Zeigt dem Disponenten den erzeugten KM-Link an.

    km_controller:
        antwort = service.erzeuge_km_anforderung(fahrzeug_id)
        return render_km_link_anzeige(antwort)

    Wir erwarten hier typischerweise:
        antwort.fahrzeug  ODER  antwort["fahrzeug"]
        antwort.link_url  ODER  antwort["link_url"] / ["link"] / ["url"]
    """

    # Versuche, fahrzeug + link_url aus dict oder Objekt zu holen
    fahrzeug = None
    link_url = None

    if isinstance(antwort, dict):
        fahrzeug = antwort.get("fahrzeug") or {}
        link_url = (
            antwort.get("link_url")
            or antwort.get("link")
            or antwort.get("url")
        )
    else:
        fahrzeug = getattr(antwort, "fahrzeug", None)
        link_url = (
            getattr(antwort, "link_url", None)
            or getattr(antwort, "link", None)
            or getattr(antwort, "url", None)
        )

    if fahrzeug is None:
        fahrzeug = {}

    # Kennzeichen ermitteln (dict oder Objekt)
    if isinstance(fahrzeug, dict):
        kennzeichen = fahrzeug.get("kennzeichen") or "Fahrzeug"
    else:
        kennzeichen = getattr(fahrzeug, "kennzeichen", "Fahrzeug")

    link_text = link_url or "(Link konnte nicht bestimmt werden)"

    inhalt = f"""
        <div class="seite-zentriert">
            <h1><a href="/dashboard">KM-Link für {kennzeichen}</a></h1>

            <p>Diesen Link kannst du an den Fahrer senden:</p>

            <div class="link-box">
                <code>{link_text}</code>
            </div>

            <div class="button-gruppe zentriert">
                <a href="/dashboard" class="btn-primar">Zurück zum Dashboard</a>
            </div>
        </div>
    """
    return layout("KM-Link erstellt", inhalt)


def render_km_historie(fahrzeug: dict, km_eintraege: List[dict]) -> str:
    """
    Zeigt die Historie der KM-Einträge für ein Fahrzeug an.

    km_controller:
        fahrzeug = service.hole_fahrzeug_details(fahrzeug_id)   -> dict
        km_eintraege = service.hole_km_historie(fahrzeug_id)    -> List[dict]
        return render_km_historie(fahrzeug, km_eintraege)

    Erwartete Keys in km_eintraege:
        "datum" (datetime), "aktueller_km", "fahrer_name", "foto_pfad"  (alle dict-basierend)
    """

    zeilen = ""

    for e in km_eintraege:
        datum_wert = e.get("datum")
        if datum_wert:
            datum_text = datum_wert.strftime("%d.%m.%Y %H:%M")
        else:
            datum_text = "-"

        km = e.get("aktueller_km", "-")
        fahrer = e.get("fahrer_name") or "-"
        foto = e.get("foto_pfad")

        if foto:
            foto_html = f'<a href="/{foto}" target="_blank">Foto</a>'
        else:
            foto_html = "-"

        zeilen += f"""
            <tr>
                <td>{datum_text}</td>
                <td>{km} km</td>
                <td>{fahrer}</td>
                <td>{foto_html}</td>
            </tr>
        """

    fahrzeug_id = fahrzeug.get("id", "")
    kennzeichen = fahrzeug.get("kennzeichen", "")

    inhalt = f"""
        <div class="seite-voll">
            <h1>
                <a href="/fahrzeug/{fahrzeug_id}/historie">
                    KM-Historie für {kennzeichen}
                </a>
            </h1>

            <table class="daten-tabelle">
                <thead>
                    <tr>
                        <th>Datum</th>
                        <th>Kilometerstand</th>
                        <th>Fahrer</th>
                        <th>Foto</th>
                    </tr>
                </thead>
                <tbody>
                    {zeilen}
                </tbody>
            </table>

            <div class="button-gruppe">
                <a href="/dashboard" class="btn-zweit">Zurück zum Dashboard</a>
            </div>
        </div>
    """
    return layout("KM-Historie", inhalt)
