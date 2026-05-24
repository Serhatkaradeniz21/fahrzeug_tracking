# base_templates.py

def layout(titel: str, inhalt: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{titel} - FahrzeugTracking</title>
        <link rel="stylesheet" href="/static/style.css">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
            }}
        </style>
    </head>
    <body>
        {inhalt}
    </body>
    </html>
    """

def fehler(text: str | None) -> str:
    if not text:
        return ""
    return f'<div class="hinweis-fehler">{text}</div>'
