-- PASO FINAL: ejecutar este script cuando el frontend/backend estén creados.
CREATE DATABASE IF NOT EXISTS universidad_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE universidad_db;

CREATE TABLE IF NOT EXISTS usuarios (
 id INT AUTO_INCREMENT PRIMARY KEY,
 username VARCHAR(30) NOT NULL UNIQUE,
 email VARCHAR(120) NOT NULL UNIQUE,
 password_hash VARCHAR(255) NOT NULL,
 rol ENUM('admin','usuario') NOT NULL DEFAULT 'usuario',
 fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 ultimo_acceso DATETIME NULL
);

CREATE TABLE IF NOT EXISTS estudiantes (
 id INT AUTO_INCREMENT PRIMARY KEY,
 nombre VARCHAR(80) NOT NULL,
 apellido VARCHAR(80) NOT NULL,
 edad TINYINT UNSIGNED NOT NULL,
 carrera VARCHAR(120) NOT NULL,
 email VARCHAR(120) NOT NULL UNIQUE,
 telefono VARCHAR(25),
 fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT chk_edad CHECK (edad BETWEEN 15 AND 100),
 INDEX idx_nombre (nombre),
 INDEX idx_apellido (apellido),
 INDEX idx_carrera (carrera)
);

CREATE TABLE IF NOT EXISTS tokens_revocados (
 jti VARCHAR(36) PRIMARY KEY,
 expiracion DATETIME NOT NULL,
 INDEX idx_expiracion (expiracion)
);

CREATE TABLE IF NOT EXISTS auditoria_estudiantes (
 id BIGINT AUTO_INCREMENT PRIMARY KEY,
 estudiante_id INT NOT NULL,
 accion ENUM('INSERT','UPDATE','DELETE') NOT NULL,
 fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS auditoria_insert;
DROP TRIGGER IF EXISTS auditoria_update;
DROP TRIGGER IF EXISTS auditoria_delete;
DELIMITER $$
CREATE TRIGGER auditoria_insert AFTER INSERT ON estudiantes FOR EACH ROW
BEGIN
 INSERT INTO auditoria_estudiantes(estudiante_id, accion) VALUES (NEW.id, 'INSERT');
END$$
CREATE TRIGGER auditoria_update AFTER UPDATE ON estudiantes FOR EACH ROW
BEGIN
 INSERT INTO auditoria_estudiantes(estudiante_id, accion) VALUES (NEW.id, 'UPDATE');
END$$
CREATE TRIGGER auditoria_delete AFTER DELETE ON estudiantes FOR EACH ROW
BEGIN
 INSERT INTO auditoria_estudiantes(estudiante_id, accion) VALUES (OLD.id, 'DELETE');
END$$
DELIMITER ;

CREATE OR REPLACE VIEW vista_estadisticas_carreras AS
SELECT carrera, COUNT(*) AS cantidad FROM estudiantes GROUP BY carrera;

-- La cuenta demo se genera con bcrypt al ejecutar crear_admin.py después de este SQL.
