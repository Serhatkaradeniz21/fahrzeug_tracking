# Test-Skript für E-Mail-Konfiguration
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Umgebungsvariablen laden
from dotenv import load_dotenv
load_dotenv()

def test_email():
    """Testet die E-Mail-Konfiguration"""
    print("=== E-Mail-Konfiguration Test ===\n")
    
    # Konfiguration ausgeben
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    empfaenger = os.getenv("DISPONENT_EMAIL", "karadeniz.serhat21@gmail.com")
    
    print(f"SMTP Server: {smtp_server}")
    print(f"SMTP Port: {smtp_port}")
    print(f"SMTP User: {smtp_user}")
    print(f"SMTP Password: {'***' if smtp_password else 'NICHT GESETZT'}")
    print(f"Empfänger: {empfaenger}")
    print()
    
    if not smtp_user or not smtp_password:
        print("❌ FEHLER: SMTP_USER oder SMTP_PASSWORD nicht in .env gesetzt!")
        print("\nBitte folgende Werte in der .env Datei eintragen:")
        print("SMTP_USER=deine_gmail@gmail.com")
        print("SMTP_PASSWORD=dein_app_passwort")
        print("\nFür Gmail benötigen Sie ein App-Passwort:")
        print("1. Gehe zu https://myaccount.google.com/security")
        print("2. Aktiviere 2-Faktor-Authentifizierung")
        print("3. Erstelle ein App-Passwort")
        return False
    
    try:
        print("Sende Test-E-Mail...")
        
        # E-Mail erstellen
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = empfaenger
        msg['Subject'] = "Test - FahrzeugTracking E-Mail"
        
        nachricht = """
Dies ist eine Test-E-Mail vom FahrzeugTracking-System.

Wenn Sie diese Nachricht erhalten, ist die E-Mail-Konfiguration korrekt.

FahrzeugTracking System
"""
        msg.attach(MIMEText(nachricht, 'plain'))
        
        # E-Mail senden
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        print("✅ E-Mail erfolgreich gesendet!")
        print(f"Bitte prüfen Sie Ihren Posteingang: {empfaenger}")
        return True
        
    except Exception as e:
        print(f"❌ FEHLER beim Senden der E-Mail: {e}")
        print("\nMögliche Lösungen:")
        print("1. Überprüfen Sie Benutzername und Passwort")
        print("2. Für Gmail: Verwenden Sie ein App-Passwort (nicht das normale Passwort)")
        print("3. Prüfen Sie, ob 2-Faktor-Authentifizierung aktiviert ist")
        print("4. Überprüfen Sie, ob die Firewall den Port 587 blockiert")
        return False

if __name__ == "__main__":
    test_email()
