use fahrzeug_tracking;
CREATE TABLE fahrzeuge (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kennzeichen VARCHAR(20) NOT NULL,
    modell VARCHAR(50),
    aktueller_km INT,
    status VARCHAR(20),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE km_anforderungen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fahrzeug_id INT,
    angeforderter_km INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fahrzeug_id) REFERENCES fahrzeuge(id)
);

CREATE TABLE km_eintraege (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fahrzeug_id INT NOT NULL,
    aktueller_km INT NOT NULL,
    fahrer_name VARCHAR(100),
    token VARCHAR(255),
    erfasst_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fahrzeug_id) REFERENCES fahrzeuge(id)
);
CREATE TABLE wartungen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fahrzeug_id INT NOT NULL,
    typ VARCHAR(100) NOT NULL,
    schwellen_km INT NOT NULL DEFAULT 0,
    intervall_km INT NULL,
    intervall_monate INT NULL,
    letztes_datum DATE NULL,
    benachrichtigung_gesendet TINYINT(1) NOT NULL DEFAULT 0,
    FOREIGN KEY (fahrzeug_id) REFERENCES fahrzeuge(id) ON DELETE CASCADE
);

