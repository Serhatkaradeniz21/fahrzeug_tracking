from typing import Optional

# base_templates.py
# Grundlegende Funktionen für das Layout und die Fehleranzeige.
#
# Ziel:
# - Einheitliches Design für alle HTML-Seiten.
# - Standardisierte Anzeige von Fehlermeldungen.
#
# Enthaltene Funktionen:
# - layout: Erzeugt das Grundlayout für HTML-Seiten.
# - fehler: Erstellt eine Fehlerbox für Fehlermeldungen.

def layout(titel: str, inhalt: str) -> str:
    """
    Erzeugt das Grundlayout für alle HTML-Seiten.
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
    Erzeugt eine standardisierte Fehlerbox für die Anzeige von Fehlermeldungen.
    """
    return f"<p class='hinweis-fehler'>{text}</p>" if text else ""