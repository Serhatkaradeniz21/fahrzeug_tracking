-- CREATE DATABASE fahrzeug_tracking;

CREATE USER 'dispo'@'localhost' IDENTIFIED BY 'dispo1234!';
GRANT ALL PRIVILEGES ON fahrzeug_tracking.* TO 'dispo'@'localhost';
FLUSH PRIVILEGES;
