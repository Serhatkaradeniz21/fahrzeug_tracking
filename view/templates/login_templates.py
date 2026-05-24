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

            <div style="text-align: center; margin-bottom: 32px;">
                <h1 style="font-size: 2.5rem; margin-bottom: 8px;">FahrzeugTracking</h1>
                <p style="color: var(--text-secondary); margin: 0;">Willkommen zurück</p>
            </div>

            {fehler(fehlermeldung)}

            <form method="post" class="formular">
                <input type="hidden" name="csrf_token" value="{csrf_token}" />

                <div class="formular-gruppe">
                    <label for="benutzername">Benutzername</label>
                    <input type="text" id="benutzername" name="benutzername" placeholder="Ihr Benutzername" required autocomplete="username" />
                </div>

                <div class="formular-gruppe">
                    <label for="passwort">Passwort</label>
                    <input type="password" id="passwort" name="passwort" placeholder="Ihr Passwort" required autocomplete="current-password" />
                </div>

                <div class="button-gruppe zentriert">
                    <button type="submit" class="btn-primar">Anmelden</button>
                </div>
            </form>

            <p style="text-align: center; margin-top: 24px; color: var(--text-secondary); font-size: 13px;">
                FahrzeugTracking System v1.0
            </p>

        </div>
    """

    return layout("Login", inhalt)
