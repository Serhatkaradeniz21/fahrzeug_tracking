# fahrzeug_templates.py

from .base_templates import layout

def render_fahrzeug_neu(csrf_token: str, hinweis: str = "") -> str:
    inhalt = f"""
        <div class="seite-zentriert">
            <div style="text-align: center; margin-bottom: 32px;">
                <h1 style="font-size: 2rem; margin-bottom: 8px;">🚗 Neues Fahrzeug anlegen</h1>
                <p style="color: var(--text-secondary); margin: 0;">Füllen Sie die Fahrzeugdaten aus</p>
            </div>

            <p class="hinweis">{hinweis}</p>

            <form method="post" class="formular">
                <input type="hidden" name="csrf_token" value="{csrf_token}" />

                <div class="formular-grid">
                    <div class="formular-gruppe">
                        <label for="kennzeichen">Kennzeichen</label>
                        <input type="text" id="kennzeichen" name="kennzeichen" placeholder="z.B. AB-CD-123" required>
                    </div>

                    <div class="formular-gruppe">
                        <label for="bezeichnung">Bezeichnung</label>
                        <input type="text" id="bezeichnung" name="bezeichnung" placeholder="z.B. VW Golf" required>
                    </div>
                </div>

                <div class="formular-grid">
                    <div class="formular-gruppe">
                        <label for="aktueller_km">Aktueller KM</label>
                        <input type="number" id="aktueller_km" name="aktueller_km_wert" placeholder="0" required>
                    </div>

                    <div class="formular-gruppe">
                        <label for="naechster_oelwechsel">Nächster Ölwechsel (KM)</label>
                        <input type="number" id="naechster_oelwechsel" name="naechster_oelwechsel_km_wert" placeholder="0" required>
                    </div>
                </div>

                <div class="formular-gruppe">
                    <label for="tuev_bis">TÜV bis</label>
                    <input type="date" id="tuev_bis" name="tuev_bis" required>
                </div>

                <div class="button-gruppe zentriert">
                    <button type="submit" class="btn-primar">💾 Speichern</button>
                    <a href="/dashboard" class="btn-zweit">Abbrechen</a>
                </div>
            </form>
        </div>
    """

    return layout("Fahrzeug anlegen", inhalt)


def render_fahrzeug_bearbeiten(fahrzeug: dict, csrf_token: str, hinweis: str = "") -> str:
    inhalt = f"""
        <div class="seite-zentriert">
            <div style="text-align: center; margin-bottom: 32px;">
                <h1 style="font-size: 2rem; margin-bottom: 8px;">✏️ Fahrzeug bearbeiten</h1>
                <p style="color: var(--text-secondary); margin: 0;">{fahrzeug['kennzeichen']} - {fahrzeug['bezeichnung']}</p>
            </div>

            <p class="hinweis">{hinweis}</p>

            <form method="post" class="formular">
                <input type="hidden" name="csrf_token" value="{csrf_token}" />

                <div class="formular-grid">
                    <div class="formular-gruppe">
                        <label for="kennzeichen">Kennzeichen</label>
                        <input type="text" id="kennzeichen" name="kennzeichen" value="{fahrzeug['kennzeichen']}" required>
                    </div>

                    <div class="formular-gruppe">
                        <label for="bezeichnung">Bezeichnung</label>
                        <input type="text" id="bezeichnung" name="bezeichnung" value="{fahrzeug['bezeichnung']}" required>
                    </div>
                </div>

                <div class="formular-grid">
                    <div class="formular-gruppe">
                        <label for="aktueller_km">Aktueller KM</label>
                        <input type="number" id="aktueller_km" name="aktueller_km_wert" value="{fahrzeug['aktueller_km']}" required>
                    </div>

                    <div class="formular-gruppe">
                        <label for="naechster_oelwechsel">Nächster Ölwechsel (KM)</label>
                        <input type="number" id="naechster_oelwechsel" name="naechster_oelwechsel_km_wert" value="{fahrzeug['naechster_oelwechsel_km']}" required>
                    </div>
                </div>

                <div class="formular-gruppe">
                    <label for="tuev_bis">TÜV bis</label>
                    <input type="date" id="tuev_bis" name="tuev_bis" value="{fahrzeug['tuev_bis']}" required>
                </div>

                <div class="button-gruppe zentriert">
                    <button type="submit" class="btn-primar">💾 Speichern</button>
                    <a href="/dashboard" class="btn-zweit">Abbrechen</a>
                </div>
            </form>
        </div>
    """

    return layout("Fahrzeug bearbeiten", inhalt)
