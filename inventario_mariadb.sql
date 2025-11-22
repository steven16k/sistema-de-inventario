SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS `sistema_inventario` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `sistema_inventario`;

CREATE TABLE IF NOT EXISTS `usuarios` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(80) NOT NULL UNIQUE,
  `password` VARCHAR(255) NOT NULL,
  `rol` ENUM('Admin','Usuario') NOT NULL DEFAULT 'Usuario',
  `email` VARCHAR(150) DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `proveedores` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(150) NOT NULL,
  `telefono` VARCHAR(30) DEFAULT NULL,
  `email` VARCHAR(150) DEFAULT NULL,
  `direccion` VARCHAR(255) DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `productos` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(150) NOT NULL,
  `descripcion` TEXT,
  `precio` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `cantidad_stock` INT NOT NULL DEFAULT 0,
  `proveedor_id` INT UNSIGNED DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`proveedor_id`) REFERENCES `proveedores`(`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  INDEX (`nombre`),
  INDEX (`proveedor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `ventas` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `fecha` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `total` DECIMAL(14,2) NOT NULL DEFAULT 0.00,
  `medio_pago` VARCHAR(60) DEFAULT 'Efectivo',
  `usuario_id` INT UNSIGNED DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios`(`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  INDEX (`fecha`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `venta_items` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `venta_id` INT UNSIGNED NOT NULL,
  `producto_id` INT UNSIGNED NOT NULL,
  `cantidad` INT NOT NULL DEFAULT 1,
  `precio_unitario` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `subtotal` DECIMAL(14,2) AS (`cantidad` * `precio_unitario`) VIRTUAL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`venta_id`) REFERENCES `ventas`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`producto_id`) REFERENCES `productos`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  INDEX (`venta_id`),
  INDEX (`producto_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `movimientos_inventario` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `producto_id` INT UNSIGNED NOT NULL,
  `fecha` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `tipo` ENUM('entrada','salida','ajuste') NOT NULL,
  `cantidad` INT NOT NULL,
  `usuario_id` INT UNSIGNED DEFAULT NULL,
  `nota` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`producto_id`) REFERENCES `productos`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios`(`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  INDEX (`producto_id`),
  INDEX (`fecha`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE OR REPLACE VIEW `vista_resumen_inventario` AS
SELECT
  p.id AS producto_id,
  p.nombre,
  p.descripcion,
  p.cantidad_stock,
  p.precio,
  (p.cantidad_stock * p.precio) AS valor_total
FROM productos p;

INSERT INTO `usuarios` (username, password, rol, email) VALUES
  ('admin', 'admin123', 'Admin', 'admin@example.com'),
  ('usuario1', 'usuario123', 'Usuario', 'user1@example.com');

INSERT INTO `proveedores` (nombre, telefono, email) VALUES
  ('Proveedor A', '555-0100', 'provA@example.com'),
  ('Proveedor B', '555-0200', 'provB@example.com');

INSERT INTO `productos` (nombre, descripcion, precio, cantidad_stock, proveedor_id) VALUES
  ('Producto X', 'Descripción X', 12.50, 100, 1),
  ('Producto Y', 'Descripción Y', 5.00, 50, 2);

DELIMITER $$
CREATE TRIGGER trg_venta_items_before_insert
BEFORE INSERT ON venta_items
FOR EACH ROW
BEGIN
  DECLARE current_stock INT;
  SELECT cantidad_stock INTO current_stock FROM productos WHERE id = NEW.producto_id FOR UPDATE;
  IF current_stock IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Producto no encontrado';
  END IF;
  IF current_stock < NEW.cantidad THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuficiente para la venta';
  END IF;
END$$

CREATE TRIGGER trg_venta_items_after_insert
AFTER INSERT ON venta_items
FOR EACH ROW
BEGIN
  UPDATE productos SET cantidad_stock = cantidad_stock - NEW.cantidad WHERE id = NEW.producto_id;
  INSERT INTO movimientos_inventario(producto_id, tipo, cantidad, usuario_id, nota)
  VALUES (NEW.producto_id, 'salida', NEW.cantidad, NULL, CONCAT('Venta id=', NEW.venta_id));
END$$

CREATE TRIGGER trg_venta_items_after_delete
AFTER DELETE ON venta_items
FOR EACH ROW
BEGIN
  UPDATE productos SET cantidad_stock = cantidad_stock + OLD.cantidad WHERE id = OLD.producto_id;
  INSERT INTO movimientos_inventario(producto_id, tipo, cantidad, usuario_id, nota)
  VALUES (OLD.producto_id, 'entrada', OLD.cantidad, NULL, CONCAT('Reversión venta id=', OLD.venta_id));
END$$

CREATE TRIGGER trg_venta_items_after_update
AFTER UPDATE ON venta_items
FOR EACH ROW
BEGIN
  DECLARE diff INT;
  DECLARE current_stock2 INT;
  SET diff = NEW.cantidad - OLD.cantidad;
  IF diff > 0 THEN
    SELECT cantidad_stock INTO current_stock2 FROM productos WHERE id = NEW.producto_id FOR UPDATE;
    IF current_stock2 < diff THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuficiente para actualizar venta';
    END IF;
    UPDATE productos SET cantidad_stock = cantidad_stock - diff WHERE id = NEW.producto_id;
    INSERT INTO movimientos_inventario(producto_id, tipo, cantidad, usuario_id, nota)
    VALUES (NEW.producto_id, 'salida', diff, NULL, CONCAT('Ajuste venta id=', NEW.venta_id));
  ELSEIF diff < 0 THEN
    UPDATE productos SET cantidad_stock = cantidad_stock + ABS(diff) WHERE id = NEW.producto_id;
    INSERT INTO movimientos_inventario(producto_id, tipo, cantidad, usuario_id, nota)
    VALUES (NEW.producto_id, 'entrada', ABS(diff), NULL, CONCAT('Ajuste venta id=', NEW.venta_id));
  END IF;
END$$
DELIMITER ;

SET FOREIGN_KEY_CHECKS = 1;

-- INSTRUCCIONES RÁPIDAS DE RESPALDO y RESTAURACIÓN (ver también README_db.md)
-- Respaldo (desde línea de comandos):
-- mysqldump -u <user> -p sistema_inventario > sistema_inventario_backup.sql
-- Restauración:
-- mysql -u <user> -p < sistema_inventario_backup.sql

-- Para exportar sólo el esquema (sin datos):
-- mysqldump -u <user> -p --no-data sistema_inventario > sistema_inventario_schema.sql
CREATE TABLE productos (
                producto_id INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                precio REAL NOT NULL,
                cantidad_stock INTEGER NOT NULL,
                proveedor TEXT
            );
INSERT INTO productos VALUES(1,'Pendrive Kingston DataTraveler 64GB','Pendrive USB 3.0 con capacidad de almacenamiento de 64GB',20000.0,20,'Kingston Technology');
INSERT INTO productos VALUES(2,'Disco Duro Externo Seagate Backup Plus 1TB','Disco duro externo portátil con capacidad de 1TB. Interfaz USB 3.0 para una rápida transferencia de datos y compatibilidad con PC y Mac',60000.0,13,'Seagate Technology');
INSERT INTO productos VALUES(3,'Tarjeta de Memoria SanDisk Ultra 128GB','Tarjeta de memoria microSDXC de alta capacidad, ideal para cámaras, smartphones y tablets. Clasificación de velocidad UHS-I Clase 10 para grabación y reproducción de video Full HD.',35600.0,29,'SanDisk Technology');
INSERT INTO productos VALUES(4,'SSD Crucial BX500 500GB','Unidad de estado sólido (SSD) de 500GB con tecnología NAND 3D. Mejora el rendimiento y la velocidad de tu computadora con tiempos de arranque más rápidos y una mayor capacidad de respuesta.',79990.0,15,'Crucial by Micron');
INSERT INTO productos VALUES(5,'Pendrive SanDisk Cruzer Glide 32GB','Pendrive USB 2.0 con capacidad de almacenamiento de 32GB. Diseño compacto y elegante con protección de deslizamiento retráctil.',13000.0,36,'SanDisk Technology');
INSERT INTO productos VALUES(6,'Tarjeta de Memoria Samsung EVO Select 256GB','Tarjeta de memoria microSDXC de 256GB de alta velocidad. Clasificación de velocidad UHS-I Clase 10 para grabación y reproducción de video 4K UHD',55000.0,8,'Samsung Electronics');
INSERT INTO productos VALUES(7,'Pendrive Corsair Flash Voyager GTX 128GB','Pendrive USB 3.1 con capacidad de almacenamiento de 128GB. Velocidades de lectura de hasta 440MB/s y escritura de hasta 440MB/s para transferencias rápidas de datos.',49870.0,28,'Corsair Memory, Inc');
INSERT INTO productos VALUES(8,'Moto corven 50hp','Esta buenisima',320000.0,89,'Corven Motos');
INSERT INTO productos VALUES(9,'Moto corven 60hp','Esta muy muy buena',400000.0,49,'Corven Motos');
INSERT INTO productos VALUES(10,'Moto corven 100hp','Es tremenda maquina',525800.0,30,'Corven Motos');
INSERT INTO productos VALUES(11,'Moto corven 300hp','Se fue a la shit',1000000.0,14,'Corven Motos');
