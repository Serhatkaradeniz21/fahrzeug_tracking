# Deployment Guide - FahrzeugTracking

## Option 1: Render.com (Empfohlen - Kostenlos & Einfach)

### Voraussetzungen
- GitHub Account
- Render.com Account (kostenlos)

### Schritte

1. **Code zu GitHub pushen**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/DEIN_USERNAME/fahrzeug-tracking.git
   git push -u origin main
   ```

2. **Render.com einrichten**
   - Gehe zu https://render.com
   - Registriere dich mit GitHub
   - Klicke auf "New +" → "Web Service"
   - Wähle dein GitHub-Repository
   - Render erkennt automatisch die `render.yaml` Datei
   - Klicke auf "Create Web Service"

3. **Umgebungsvariablen konfigurieren**
   Im Render Dashboard unter "Environment" folgende Variablen setzen:
   ```
   DB_HOST = DEINE_MYSQL_HOST
   DB_PORT = 3306
   DB_USER = DEIN_MYSQL_USER
   DB_PASSWORD = DEIN_MYSQL_PASSWORT
   DB_NAME = tracking
   SECRET_KEY = EIN_LANGE_ZUFALLIGER_STRING
   DISPONENT_USER = disponent
   DISPONENT_PASS = DEIN_PASSWORT
   ```

4. **Datenbank einrichten**
   - Nutze einen kostenlosen MySQL-Service wie:
     - PlanetScale (kostenlos)
     - Railway MySQL (kostenlos)
     - Oder Render PostgreSQL (kostenlos, aber Code-Anpassung nötig)

5. **Domain konfigurieren**
   - Render gibt dir eine URL wie: `https://fahrzeug-tracking.onrender.com`
   - Für eigene Domain: "Settings" → "Domains" → Domain hinzufügen

## Option 2: PythonAnywhere (Kostenlos)

### Schritte

1. **PythonAnywhere Account erstellen**
   - Gehe zu https://www.pythonanywhere.com
   - Registriere dich (kostenloser "Beginner" Account)

2. **Web App erstellen**
   - "Web" → "Add a new web app"
   - Wähle "Manual Configuration"
   - Python Version: 3.10+
   - Domain: `deinname.pythonanywhere.com`

3. **Code hochladen**
   - "Files" → "Upload a file"
   - Oder via Git/SFTP

4. **Virtual Environment erstellen**
   ```bash
   mkvirtualenv fahrzeug-tracking
   pip install -r requirements.txt
   ```

5. **WSGI konfigurieren**
   In `wsgi.py`:
   ```python
   from hauptprogramm import app
   application = app
   ```

6. **Umgebungsvariablen setzen**
   - "Web" → "WSGI configuration file"
   - "Variables" → Environment Variables hinzufügen

## Option 3: Eigener VPS (DigitalOcean/Hetzner)

### Voraussetzungen
- VPS mit Ubuntu 20.04+
- Domain (z.B. bei Namecheap, GoDaddy)

### Schritte

1. **VPS einrichten**
   ```bash
   # Updates
   sudo apt update && sudo apt upgrade -y
   
   # Python installieren
   sudo apt install python3 python3-pip python3-venv -y
   
   # MySQL installieren
   sudo apt install mysql-server -y
   ```

2. **Code deployen**
   ```bash
   git clone https://github.com/DEIN_USERNAME/fahrzeug-tracking.git
   cd fahrzeug-tracking
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Systemd Service erstellen**
   ```bash
   sudo nano /etc/systemd/system/fahrzeug-tracking.service
   ```
   
   Inhalt:
   ```ini
   [Unit]
   Description=FahrzeugTracking API
   After=network.target
   
   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/fahrzeug-tracking
   ExecStart=/home/ubuntu/fahrzeug-tracking/venv/bin/uvicorn hauptprogramm:app --host 0.0.0.0 --port 8000
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   ```bash
   sudo systemctl enable fahrzeug-tracking
   sudo systemctl start fahrzeug-tracking
   ```

4. **Nginx als Reverse Proxy**
   ```bash
   sudo apt install nginx -y
   sudo nano /etc/nginx/sites-available/fahrzeug-tracking
   ```
   
   Inhalt:
   ```nginx
   server {
       listen 80;
       server_name deine-domain.de;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /static {
           alias /home/ubuntu/fahrzeug-tracking/static;
       }
       
       location /uploads {
           alias /home/ubuntu/fahrzeug-tracking/uploads;
       }
   }
   ```
   
   ```bash
   sudo ln -s /etc/nginx/sites-available/fahrzeug-tracking /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

5. **SSL mit Let's Encrypt**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d deine-domain.de
   ```

## WICHTIG: Sicherheit für Produktion

1. **Starkes SECRET_KEY verwenden**
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```

2. **HTTPS erzwingen**
   - SSL-Zertifikat installieren
   - HTTP zu HTTPS Redirect

3. **Datenbank-Zugriff einschränken**
   - Nur localhost oder IP-Whitelist
   - Starkes Passwort

4. **Regelmäßige Backups**
   - Datenbank-Backups automatisieren

5. **Firewall konfigurieren**
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

## Empfehlung für den Anfang

Starte mit **Render.com** - es ist:
- Kostenlos für kleine Anwendungen
- Automatisches Deploy bei GitHub Push
- HTTPS automatisch
- Einfache Domain-Konfiguration
- Keine Server-Administration nötig
