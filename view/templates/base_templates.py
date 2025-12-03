# base_templates.py

def layout(titel: str, inhalt: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{titel}</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            {inhalt}
        </div>
    </body>
    </html>
    """

def fehler(text: str | None) -> str:
    if not text:
        return ""
    return f'<div class="fehlermeldung">{text}</div>'
