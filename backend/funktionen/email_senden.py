import secrets
import smtplib
from email.message import EmailMessage
from datetime import datetime
from modelle.km_token import TokenEintrag

def erstelle_token():
    return secrets.token_urlsafe(32)

def sende_km_link(email_empfaenger):
    token = erstelle_token()

    # Eintrag simulieren (später DB!)
    token_obj = TokenEintrag(
        token=token,
        fahrer_email=email_empfaenger,
        erstellt_am=datetime.now()
    )

    link = f"http://localhost:8000/formular/{token}"

    nachricht = EmailMessage()
    nachricht['Subject'] = 'Bitte Kilometerstand eintragen'
    nachricht['From'] = 'tracking@primafahrten.de'
    nachricht['To'] = email_empfaenger
    nachricht.set_content(f"Klicke hier, um deinen Kilometerstand einzugeben:\n{link}")

    # SMTP-Verbindung (z. B. Gmail oder lokal)
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('deine.email@gmail.com', 'deinpasswort')
        smtp.send_message(nachricht)

    print("Token versendet:", token)
    return token_obj
