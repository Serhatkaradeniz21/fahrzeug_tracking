# login_templates.py
# Template für die Login-Seite

from typing import Optional
from .base_templates import layout, fehler


def render_login_seite(csrf_token: str, fehlermeldung: Optional[str] = None) -> str:
    """
    Rendert die Login-Seite mit CSRF-Token und optionaler Fehlermeldung.
    """

    inhalt = f"""
        <div class="seite-zentriert">

            <h1><a href="/login">FahrzeugTracking – Login</a></h1>

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
