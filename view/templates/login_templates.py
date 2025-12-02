# login_templates.py
# Funktionen zur Erstellung der Login-Seite.
#
# Ziel:
# - Bereitstellung eines sicheren Login-Formulars.
# - Einbindung von CSRF-Schutz.
#
# Enthaltene Funktionen:
# - render_login_seite: Erstellt die HTML-Seite für den Login-Bereich.

from .base_templates import layout, fehler
from typing import Optional

def render_login_seite(csrf_token: str, fehlermeldung: Optional[str] = None) -> str:
    """
    Erstellt die HTML-Seite für den Login-Bereich.
    """
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