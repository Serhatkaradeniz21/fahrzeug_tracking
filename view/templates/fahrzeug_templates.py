# fahrzeug_templates.py

from .base_templates import layout

def render_fahrzeug_neu(csrf_token: str, hinweis: str = "") -> str:
    inhalt = f"""
        <div class="seite-zentriert">
            <h1><a href="/fahrzeug/neu">Fahrzeug anlegen</a></h1>

            <p class="hinweis">{hinweis}</p>

            <form method="post" class="formular">
                <input type="hidden" name="csrf_token" value="{csrf_token}" />

                <div class="formular-gruppe">
                    <label>Kennzeichen:</label>
                    <input type="text" name="kennzeichen" required>
                </div>

                <div class="formular-gruppe">
                    <label>Bezeichnung:</label>
                    <input type="text" name="bezeichnung" required>
                </div>

                <div class="formular-gruppe">
                    <label>Aktueller KM:</label>
                    <input type="number" name="aktueller_km_wert" required>
                </div>

                <div class="formular-gruppe">
                    <label>TÜV bis:</label>
                    <input type="date" name="tuev_bis" required>
                </div>

                <div class="formular-gruppe">
                    <label>Nächster Ölwechsel (KM):</label>
                    <input type="number" name="naechster_oelwechsel_km_wert" required>
                </div>

                <button class="btn-primar">Speichern</button>
            </form>
        </div>
    """

    return layout("Fahrzeug anlegen", inhalt)


def render_fahrzeug_bearbeiten(fahrzeug: dict, csrf_token: str, hinweis: str = "") -> str:
    inhalt = f"""
        <div class="seite-zentriert">

            <h1><a href="/fahrzeug/{fahrzeug['id']}/bearbeiten">Fahrzeug bearbeiten</a></h1>

            <p class="hinweis">{hinweis}</p>

            <form method="post" class="formular">
                <input type="hidden" name="csrf_token" value="{csrf_token}" />

                <div class="formular-gruppe">
                    <label>Kennzeichen:</label>
                    <input type="text" name="kennzeichen" value="{fahrzeug['kennzeichen']}" required>
                </div>

                <div class="formular-gruppe">
                    <label>Bezeichnung:</label>
                    <input type="text" name="bezeichnung" value="{fahrzeug['bezeichnung']}" required>
                </div>

                <div class="formular-gruppe">
                    <label>Aktueller KM:</label>
                    <input type="number" name="aktueller_km_wert" value="{fahrzeug['aktueller_km']}" required>
                </div>

                <div class="formular-gruppe">
                    <label>TÜV bis:</label>
                    <input type="date" name="tuev_bis" value="{fahrzeug['tuev_bis']}" required>
                </div>

                <div class="formular-gruppe">
                    <label>Nächster Ölwechsel (KM):</label>
                    <input type="number" name="naechster_oelwechsel_km_wert" value="{fahrzeug['naechster_oelwechsel_km']}" required>
                </div>

                <button class="btn-primar">Speichern</button>
            </form>
        </div>
    """

    return layout("Fahrzeug bearbeiten", inhalt)
