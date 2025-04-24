-- BASE DE DATOS EN DJANGO
CREATE DATABASE autorentleon;
USE autorentleon;

SELECT * FROM auth_user;
SELECT * FROM users_metadata;

select * from user_control_historicalusersmetadata;
select * from error_log_errorlog;

SET SQL_SAFE_UPDATES = 0;
UPDATE users_metadata
SET user_image = 'hola.png'
WHERE user_image IS NULL OR user_image = '';
SET SQL_SAFE_UPDATES = 1;

UPDATE auth_user
SET is_active = 1
WHERE id = 12;


INSERT INTO users_metadata (user_id, user_image) VALUES
(1, 'hola.png')


-- --------------------------------------------------------------------------------------------------------------------
-- BASE DE DATOS DE REFERENCIA PARA EL SISTEMA
-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS alquiler_vehiculos;
USE alquiler_vehiculos;

-- Tabla de Tipos de Vehículos
CREATE TABLE tipos_vehiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de Marcas
CREATE TABLE marcas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de Sucursales
CREATE TABLE sucursales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion TEXT NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    horario_apertura TIME,
    horario_cierre TIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de Vehículos
CREATE TABLE vehiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_vehiculo_id INT NOT NULL,
    marca_id INT NOT NULL,
    modelo VARCHAR(100) NOT NULL,
    año INT NOT NULL,
    placa VARCHAR(20) NOT NULL,
    color VARCHAR(50) NOT NULL,
    capacidad_pasajeros INT NOT NULL,
    estado ENUM('disponible', 'alquilado', 'mantenimiento') DEFAULT 'disponible',
    sucursal_actual_id INT NOT NULL,
    precio_diario DECIMAL(10, 2) NOT NULL,
    foto_principal VARCHAR(255),
    descripcion TEXT,
    fecha_adquisicion DATE,
    kilometraje_actual INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (tipo_vehiculo_id) REFERENCES tipos_vehiculos(id),
    FOREIGN KEY (marca_id) REFERENCES marcas(id),
    FOREIGN KEY (sucursal_actual_id) REFERENCES sucursales(id)
);

-- Tabla de Clientes
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    tipo_documento ENUM('DUI', 'pasaporte') NOT NULL,
    numero_documento VARCHAR(50) NOT NULL,
    direccion TEXT NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    tipo_cliente ENUM('nacional', 'extranjero') NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    status ENUM('activo', 'inactivo', 'lista_negra') DEFAULT 'activo',
    notas TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY (tipo_documento, numero_documento)
);

-- Tabla de Referencias Cliente
CREATE TABLE referencias_cliente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    parentesco VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

-- Tabla de Usuarios (para registrar quién realiza las inspecciones/pagos)
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    rol ENUM('administrador', 'empleado') NOT NULL,
    sucursal_id INT,
    estado ENUM('activo', 'inactivo') DEFAULT 'activo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id)
);

-- Tabla de Alquileres
CREATE TABLE alquileres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    vehiculo_id INT NOT NULL,
    sucursal_entrega_id INT NOT NULL,
    sucursal_devolucion_id INT NOT NULL,
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME NOT NULL,
    fecha_devolucion_real DATETIME,
    estado ENUM('reservado', 'activo', 'finalizado', 'retrasado') DEFAULT 'reservado',
    precio_total DECIMAL(10, 2) NOT NULL,
    deposito DECIMAL(10, 2) NOT NULL,
    combustible_entrega ENUM('vacio', '1/4', '1/2', '3/4', 'lleno') NOT NULL,
    combustible_devolucion ENUM('vacio', '1/4', '1/2', '3/4', 'lleno'),
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id),
    FOREIGN KEY (sucursal_entrega_id) REFERENCES sucursales(id),
    FOREIGN KEY (sucursal_devolucion_id) REFERENCES sucursales(id)
);

-- Tabla de Inspecciones
CREATE TABLE inspecciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alquiler_id INT NOT NULL,
    tipo ENUM('entrega', 'devolucion') NOT NULL,
    fecha DATETIME NOT NULL,
    usuario_id INT NOT NULL,
    estado_general ENUM('excelente', 'bueno', 'regular', 'malo') NOT NULL,
    combustible ENUM('vacio', '1/4', '1/2', '3/4', 'lleno') NOT NULL,
    kilometraje INT NOT NULL,
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (alquiler_id) REFERENCES alquileres(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla de Detalles de Inspección
CREATE TABLE detalles_inspeccion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspeccion_id INT NOT NULL,
    parte_vehiculo VARCHAR(100) NOT NULL,
    estado ENUM('excelente', 'bueno', 'regular', 'malo', 'dañado') NOT NULL,
    descripcion TEXT,
    foto_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (inspeccion_id) REFERENCES inspecciones(id)
);

-- Tabla de Pagos
CREATE TABLE pagos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alquiler_id INT NOT NULL,
    usuario_id INT NOT NULL,
    monto DECIMAL(10, 2) NOT NULL,
    tipo_pago ENUM('efectivo', 'tarjeta_credito', 'tarjeta_debito') NOT NULL,
    fecha_pago DATETIME NOT NULL,
    concepto ENUM('anticipo', 'pago_final', 'cargo_adicional', 'reembolso') NOT NULL,
    referencia VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (alquiler_id) REFERENCES alquileres(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla de Mantenimientos
CREATE TABLE mantenimientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehiculo_id INT NOT NULL,
    tipo_mantenimiento VARCHAR(100) NOT NULL,
    fecha DATE NOT NULL,
    kilometraje INT NOT NULL,
    costo DECIMAL(10, 2) NOT NULL,
    descripcion TEXT,
    proveedor VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id)
);

-- Tabla de Facturas
CREATE TABLE facturas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alquiler_id INT NOT NULL,
    numero_factura VARCHAR(50) NOT NULL UNIQUE,
    fecha_emision DATETIME NOT NULL,
    monto_total DECIMAL(10, 2) NOT NULL,
    estado ENUM('emitida', 'pagada', 'anulada') DEFAULT 'emitida',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (alquiler_id) REFERENCES alquileres(id)
);

-- Añadir algunos datos iniciales para pruebas
INSERT INTO tipos_vehiculos (nombre, descripcion) VALUES 
('Sedan', 'Vehículo de 4 puertas con cajuela separada'),
('Camioneta', 'Vehículo tipo SUV con mayor espacio'),
('Pick-up', 'Vehículo con área de carga trasera descubierta');

INSERT INTO marcas (nombre) VALUES 
('Toyota'),
('Honda'),
('Nissan'),
('Ford'),
('Hyundai');

INSERT INTO sucursales (nombre, direccion, telefono, email, horario_apertura, horario_cierre) VALUES 
('Sucursal Central', 'Av. Principal #123, Ciudad Central', '2222-1111', 'central@rentacar.com', '08:00:00', '18:00:00'),
('Sucursal Norte', 'Blvd. Norte #456, Zona Norte', '2222-2222', 'norte@rentacar.com', '08:00:00', '18:00:00'),
('Sucursal Aeropuerto', 'Terminal Aérea Internacional, Local 12', '2222-3333', 'aeropuerto@rentacar.com', '06:00:00', '22:00:00');

-- Añadir usuarios
INSERT INTO usuarios (nombre, apellido, email, password, rol, sucursal_id) VALUES
('Admin', 'Sistema', 'admin@rentacar.com', '$2y$10$abcdefghijklmnopqrstuv', 'administrador', 1),
('Juan', 'Pérez', 'juan@rentacar.com', '$2y$10$abcdefghijklmnopqrstuv', 'empleado', 1),
('María', 'López', 'maria@rentacar.com', '$2y$10$abcdefghijklmnopqrstuv', 'empleado', 2);

-- Añadir vehículos
INSERT INTO vehiculos (tipo_vehiculo_id, marca_id, modelo, año, placa, color, capacidad_pasajeros, sucursal_actual_id, precio_diario, descripcion, fecha_adquisicion, kilometraje_actual) VALUES
(1, 1, 'Corolla', 2023, 'P123456', 'Blanco', 5, 1, 45.00, 'Toyota Corolla SE, económico y confortable', '2023-01-15', 5000),
(1, 2, 'Civic', 2022, 'P234567', 'Negro', 5, 1, 48.00, 'Honda Civic Touring, equipado con extras', '2022-06-10', 12000),
(2, 1, 'RAV4', 2023, 'P345678', 'Azul', 5, 2, 65.00, 'Toyota RAV4 AWD, ideal para viajes', '2023-02-20', 7500),
(3, 4, 'Ranger', 2022, 'P456789', 'Gris', 5, 3, 75.00, 'Ford Ranger XLT, para trabajo y aventuras', '2022-08-05', 9000);