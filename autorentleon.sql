-- BASE DE DATOS EN DJANGO
CREATE DATABASE autorentleon;
USE autorentleon;

SELECT * FROM auth_user;
SELECT * FROM users_metadata;
SELECT * FROM error_log_errorlog;
SELECT * FROM auth_permission;
SELECT * FROM auth_historicaluser;
SELECT * FROM django_session;
SELECT * FROM django_content_type;
SELECT * FROM branch;
SELECT * FROM vehicleimage;
SELECT * FROM vehicle;
SELECT * FROM brand;
SELECT * FROM vehiclemodel;
SELECT * FROM vehiclecategory;
SELECT * FROM django_migrations;

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

UPDATE branch
SET active = 1
WHERE id = 1;

UPDATE branch
SET modified_by = 1
WHERE id = 1;

UPDATE auth_user
SET is_staff = 1
WHERE id = 33;

SET SQL_SAFE_UPDATES = 0;
DELETE FROM vehicleimage;
DELETE FROM vehicle;
SET SQL_SAFE_UPDATES = 1;

UPDATE brand
SET name = "Toyoda"
WHERE id = 1;

INSERT INTO users_metadata (user_id, user_image) VALUES
(1, 'hola.png');

-- tablas para departamentos, municipios y distritos
create table department( -- departamentos
  id int primary key auto_increment not null,
  code INT not null,
  department varchar(255) not null,
  active BOOLEAN DEFAULT TRUE,
  created_by VARCHAR(50),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  modified_by VARCHAR(50),
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO department (code, department, active, created_by, created_at, modified_by, updated_at) VALUES
(1, 'Ahuachapán', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(2, 'Santa Ana', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(3, 'Sonsonate', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(4, 'Chalatenango', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(5, 'La Libertad', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(6, 'San Salvador', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(7, 'Cuscatlán', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(8, 'La Paz', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(9, 'Cabañas', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(10, 'San Vicente', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(11, 'Usulután', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(12, 'San Miguel', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(13, 'Morazán', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(14, 'La Unión', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);

-- Nuevos INSERT para la tabla 'municipality'
INSERT INTO municipality (code, municipality, department_id, active, created_by, created_at, modified_by, updated_at) VALUES
(101, 'Ahuachapán Centro', 1, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(102, 'Ahuachapán Norte', 1, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(103, 'Ahuachapán Sur', 1, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(201, 'Santa Ana Centro', 2, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(202, 'Santa Ana Este', 2, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(203, 'Santa Ana Norte', 2, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(204, 'Santa Ana Oeste', 2, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(301, 'Sonsonate Centro', 3, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(302, 'Sonsonate Este', 3, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(303, 'Sonsonate Norte', 3, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(304, 'Sonsonate Oeste', 3, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(401, 'Chalatenango Centro', 4, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(402, 'Chalatenango Norte', 4, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(403, 'Chalatenango Sur', 4, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(501, 'La Libertad Centro', 5, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(502, 'La Libertad Costa', 5, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(503, 'La Libertad Este', 5, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(504, 'La Libertad Norte', 5, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(505, 'La Libertad Oeste', 5, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(506, 'La Libertad Sur', 5, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(601, 'San Salvador Centro', 6, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(602, 'San Salvador Este', 6, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(603, 'San Salvador Norte', 6, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(604, 'San Salvador Oeste', 6, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(605, 'San Salvador Sur', 6, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(701, 'Cuscatlán Norte', 7, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(702, 'Cuscatlán Sur', 7, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(801, 'La Paz Centro', 8, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(802, 'La Paz Este', 8, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(803, 'La Paz Oeste', 8, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(901, 'Cabañas Este', 9, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(902, 'Cabañas Oeste', 9, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(1001, 'San Vicente Norte', 10, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(1002, 'San Vicente Sur', 10, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(1101, 'Usulután Este', 11, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(1102, 'Usulután Norte', 11, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(1103, 'Usulután Oeste', 11, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(1201, 'San Miguel Centro', 12, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(1202, 'San Miguel Norte', 12, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(1203, 'San Miguel Oeste', 12, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(1301, 'Morazán Norte', 13, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(1302, 'Morazán Sur', 13, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(1401, 'La Unión Norte', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(1402, 'La Unión Sur', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP);

-- Nuevos INSERT para la tabla 'disctrict' (según tu DDL)
INSERT INTO disctrict (code, district, municipality_id, active, created_by, created_at, modified_by, updated_at) VALUES
(10101, 'Ahuachapán', 1, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(10102, 'Apaneca', 1, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(10104, 'Concepción de Ataco', 1, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(10111, 'Tacuba', 1, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(10203, 'Atiquizaya', 2, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(10205, 'El Refugio', 2, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(10209, 'San Lorenzo', 2, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(10212, 'Turín', 2, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(10306, 'Guaymango', 3, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(10307, 'Jujutla', 3, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(10308, 'San Francisco Menéndez', 3, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(10310, 'San Pedro Puxtla', 3, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(20110, 'Santa Ana', 4, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(20202, 'Coatepeque', 5, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(20204, 'El Congo', 5, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(20306, 'Masahuat', 6, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(20307, 'Metapán', 6, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(20311, 'Santa Rosa Guachipilín', 6, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(20313, 'Texistepeque', 6, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(20401, 'Candelaria de la Frontera', 7, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(20403, 'Chalchuapa', 7, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(20405, 'El Porvenir', 7, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(20408, 'San Antonio Pajonal', 7, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(20409, 'San Sebastián Salitrillo', 7, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(20412, 'Santiago de la Frontera', 7, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(30109, 'Nahulingo', 8, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(30111, 'San Antonio del Monte', 8, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(30114, 'Santo Domingo de Guzmán', 8, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(30115, 'Sonsonate', 8, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(30116, 'Sonzacate', 8, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(30202, 'Armenia', 9, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(30203, 'Caluco', 9, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(30204, 'Cuisnahuat', 9, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(30205, 'Santa Isabel Ishuatán', 9, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(30206, 'Izalco', 9, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(30212, 'San Julián', 9, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(30307, 'Juayúa', 10, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(30308, 'Nahuizalco', 10, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(30310, 'Salcoatitán', 10, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(30313, 'Santa Catarina Masahuat', 10, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(30401, 'Acajutla', 11, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40101, 'Agua Caliente', 12, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40108, 'Dulce Nombre de María', 12, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40110, 'El Paraíso', 12, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40113, 'La Reina', 12, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40116, 'Nueva Concepción', 12, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40122, 'San Fernando', 12, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40124, 'San Francisco Morazán', 12, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40131, 'San Rafael', 12, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40132, 'Santa Rita', 12, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40133, 'Tejutla', 12, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40204, 'Citalá', 13, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40225, 'San Ignacio', 13, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40212, 'La Palma', 13, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40302, 'Arcatao', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40303, 'Azacualpa', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40305, 'Comalapa', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40306, 'Concepción Quezaltepeque', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40307, 'Chalatenango', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40309, 'El Carrizal', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40311, 'La Laguna', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40314, 'Las Vueltas', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40315, 'Nombre de Jesús', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40317, 'Nueva Trinidad', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40318, 'Ojos de Agua', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40319, 'Potonico', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40320, 'San Antonio de la Cruz', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40321, 'San Antonio Los Ranchos', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40326, 'San Isidro Labrador', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40323, 'San Francisco Lempa', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40327, 'San José Cancasque / Cancasque', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40328, 'San José Las Flores / Las Flores', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40329, 'San Luis del Carmen', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(40330, 'San Miguel de Mercedes', 14, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50102, 'Ciudad Arce', 15, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50115, 'San Juan Opico', 15, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50205, 'Chiltiupán', 16, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50208, 'Jicalapa', 16, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50209, 'La Libertad', 16, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50218, 'Tamanique', 16, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50220, 'Teotepeque', 16, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50301, 'Antiguo Cuscatlán', 17, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50306, 'Huizúcar', 17, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50310, 'Nuevo Cuscatlán', 17, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50314, 'San José Villanueva', 17, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50322, 'Zaragoza', 17, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50412, 'Quezaltepeque', 18, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50416, 'San Matías', 18, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50417, 'San Pablo Tacachico', 18, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50503, 'Colón', 19, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50507, 'Jayaque', 19, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50513, 'Sacacoyo', 19, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50519, 'Talnique', 19, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50521, 'Tepecoyo', 19, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50604, 'Comasagua', 20, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(50611, 'Santa Tecla antes: Nueva San Salvador', 20, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(60103, 'Ayutuxtepeque', 21, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(60104, 'Cuscatancingo', 21, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(60108, 'Mejicanos', 21, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(60114, 'San Salvador', 21, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(60119, 'Delgado', 21, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(60207, 'Ilopango', 22, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(60213, 'San Martín', 22, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(60217, 'Soyapango', 22, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(60218, 'Tonacatepeque', 22, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(60301, 'Aguilares', 23, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(60305, 'El Paisnal', 23, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(60306, 'Guazapa', 23, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(60402, 'Apopa', 24, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(60409, 'Nejapa', 24, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(60510, 'Panchimalco', 25, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(60511, 'Rosario de Mora', 25, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(60512, 'San Marcos', 25, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(60515, 'Santiago Texacuangos', 25, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(60516, 'Santo Tomás', 25, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(70106, 'Oratorio de Concepción', 26, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(70107, 'San Bartolomé Perulapía', 26, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(70109, 'San José Guayabal', 26, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(70110, 'San Pedro Perulapán', 26, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(70115, 'Suchitoto', 26, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(70201, 'Candelaria', 27, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(70202, 'Cojutepeque', 27, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(70203, 'El Carmen', 27, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(70204, 'El Rosario', 27, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(70205, 'Monte San Juan', 27, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(70208, 'San Cristóbal', 27, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(70211, 'San Rafael Cedros', 27, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(70212, 'San Ramón', 27, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(70213, 'Santa Cruz Analquito', 27, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(70214, 'Santa Cruz Michapa', 27, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(70216, 'Tenancingo', 27, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80102, 'El Rosario / Rosario de La Paz', 28, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80103, 'Jerusalén', 28, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80104, 'Mercedes La Ceiba', 28, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80106, 'Paraíso de Osorio', 28, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80107, 'San Antonio Masahuat', 28, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80108, 'San Emigdio', 28, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80112, 'San Juan Tepezontes', 28, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80114, 'San Miguel Tepezontes', 28, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80116, 'San Pedro Nonualco', 28, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80118, 'Santa María Ostuma', 28, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80119, 'Santiago Nonualco', 28, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80122, 'San Luis La Herradura', 28, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80210, 'San Juan Nonualco', 29, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80217, 'San Rafael Obrajuelo', 29, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80221, 'Zacatecoluca', 29, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80301, 'Cuyultitán', 30, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80305, 'Olocuilta', 30, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80309, 'San Francisco Chinameca', 30, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80311, 'San Juan Talpa', 30, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80313, 'San Luis Talpa', 30, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80315, 'San Pedro Masahuat', 30, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(80320, 'Tapalhuaca', 30, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(90109, 'Dolores / Villa Dolores', 31, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(90102, 'Guacotecti', 31, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(90105, 'San Isidro', 31, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(90106, 'Sensuntepeque', 31, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(90108, 'Victoria', 31, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(90201, 'Cinquera', 32, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(90203, 'Ilobasco', 32, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(90204, 'Jutiapa', 32, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(90207, 'Tejutepeque', 32, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(100101, 'Apastepeque', 33, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(100106, 'San Esteban Catarina', 33, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(100107, 'San Ildefonso', 33, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(100108, 'San Lorenzo', 33, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(100109, 'San Sebastián', 33, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(100104, 'Santa Clara', 33, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(100105, 'Santo Domingo', 33, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(100202, 'Guadalupe', 34, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(100203, 'San Cayetano Istepeque', 34, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(100210, 'San Vicente', 34, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(100211, 'Tecoluca', 34, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(100212, 'Tepetitán', 34, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(100213, 'Verapaz', 34, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110103, 'California', 35, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110104, 'Concepción Batres', 35, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110106, 'Ereguayquín', 35, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110110, 'Jucuarán', 35, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110113, 'Ozatlán', 35, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110123, 'Usulután', 35, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110117, 'San Dionisio', 35, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110118, 'Santa Elena', 35, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110120, 'Santa María', 35, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110122, 'Tecapán', 35, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110201, 'Alegría', 36, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110202, 'Berlín', 36, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110205, 'El Triunfo', 36, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110207, 'Estanzuelas', 36, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110209, 'Jucuapa', 36, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110211, 'Mercedes Umaña', 36, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110212, 'Nueva Granada', 36, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110216, 'San Buenaventura', 36, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110221, 'Santiago de María', 36, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110308, 'Jiquilisco', 37, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110314, 'Puerto El Triunfo', 37, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110315, 'San Agustín', 37, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(110319, 'San Francisco Javier', 37, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120103, 'Comacarán', 38, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120109, 'Moncagua', 38, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120106, 'Chirilagua', 38, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120112, 'Quelepa', 38, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120117, 'San Miguel', 38, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120120, 'Uluazapa', 38, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120201, 'Carolina', 39, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120202, 'Ciudad Barrios', 39, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120204, 'Chapeltique', 39, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120211, 'Nuevo Edén de San Juan', 39, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120213, 'San Antonio del Mosco', 39, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120214, 'San Gerardo', 39, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120216, 'San Luis de La Reina', 39, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120219, 'Sesori', 39, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120305, 'Chinameca', 40, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120307, 'El Tránsito', 40, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120308, 'Lolotique', 40, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120310, 'Nueva Guadalupe', 40, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120315, 'San Jorge', 40, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(120318, 'San Rafael Oriente', 40, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130101, 'Arambala', 41, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130102, 'Cacaopera', 41, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130103, 'Corinto', 41, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130107, 'El Rosario', 41, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130110, 'Joateca', 41, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130111, 'Jocoaitique', 41, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130114, 'Meanguera', 41, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130116, 'Perquín', 41, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130118, 'San Fernando', 41, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130120, 'San Isidro', 41, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130124, 'Torola', 41, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130204, 'Chilanga', 42, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130205, 'Delicias de Concepción', 42, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130206, 'El Divisadero', 42, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130208, 'Gualococti', 42, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130209, 'Guatajiagua', 42, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130212, 'Jocoro', 42, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130213, 'Lolotiquillo', 42, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130215, 'Osicala', 42, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130217, 'San Carlos', 42, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130219, 'San Francisco Gotera', 42, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130221, 'San Simón', 42, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130222, 'Sensembra', 42, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130223, 'Sociedad', 42, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130225, 'Yamabal', 42, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(130226, 'Yoloaiquín', 42, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(140101, 'Anamorós', 43, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(140102, 'Bolívar', 43, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(140103, 'Concepción de Oriente', 43, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(140106, 'El Sauce', 43, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(140109, 'Lislique', 43, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(140111, 'Nueva Esparta', 43, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(140112, 'Pasaquina', 43, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(140113, 'Polorós', 43, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(140115, 'San José La Fuente', 43, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(140116, 'Santa Rosa de Lima', 43, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(140204, 'Conchagua', 44, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(140205, 'El Carmen', 44, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(140207, 'Intipucá', 44, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(140208, 'La Unión', 44, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(140210, 'Meanguera del Golfo', 44, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(140214, 'San Alejo', 44, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(140217, 'Yayantique', 44, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(140218, 'Yucuaiquín', 44, TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP);

create table municipality( -- municipios
  id int primary key auto_increment not null,
  code INT not null,
  municipality varchar(255) not null,
  department_id int not null,
  active BOOLEAN DEFAULT TRUE,
  created_by VARCHAR(50),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  modified_by VARCHAR(50),
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  foreign key (department_id) references department(id) on delete cascade on update cascade 
);

create table district( -- distritos
  id int primary key auto_increment not null,
  code INT not null,
  district varchar(255) not null,
  municipality_id int not null,
  active BOOLEAN DEFAULT TRUE,
  created_by VARCHAR(50),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  modified_by VARCHAR(50),
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  foreign key (municipality_id) references municipality(id) on delete cascade on update cascade
);

-- 1. COMPANY
CREATE TABLE company (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trade_name VARCHAR(100),
    nrc VARCHAR(50),
    classification ENUM('pequeña', 'mediana', 'gran'),
    phone VARCHAR(20),
    address TEXT,
    logo_url VARCHAR(255),
    email VARCHAR(100),
    website VARCHAR(100),
    active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified_by VARCHAR(50),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. BRANCH
CREATE TABLE branch (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    district_id INT,
    email VARCHAR(100),
    active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified_by VARCHAR(50),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (district_id) REFERENCES district(id)
);
CREATE TABLE branch (id INT);
DROP TABLE branch;
SET SQL_SAFE_UPDATES = 0;
DELETE FROM django_migrations WHERE app='branch';
SET SQL_SAFE_UPDATES = 1;

INSERT INTO branch (name, phone, address, district_id, email, active, created_by, created_at, modified_by, updated_at) VALUES
(
    'Sucursal Central Apopa',
    '+503 2215-1020',
    'Avenida Quirino Chávez #45, Barrio El Centro, Apopa, San Salvador',
    1, -- Asegúrate que el District con ID 1 exista (ej. Ahuachapán distrito)
    'central.apopa@miempresa.com.sv',
    TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP
),
(
    'Agencia Santa Tecla Las Delicias',
    '+503 2228-4578',
    'Centro Comercial Las Delicias, Local 12B, Carretera Panamericana, Santa Tecla, La Libertad',
    5, -- Asegúrate que el District con ID 5 exista (ej. Atiquizaya)
    's.tecla.delicias@miempresa.com.sv',
    TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP
),
(
    'Punto de Venta San Miguel Roosevelt',
    '+503 2661-3399',
    'Avenida Roosevelt Sur, Edificio Comercial La Confianza, San Miguel',
    10, -- Asegúrate que el District con ID 10 exista (ej. Jujutla)
    'sanmiguel.roosevelt@miempresa.com.sv',
    TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP
),
(
    'Oficina Sonsonate El Progreso',
    '+503 2451-8870',
    'Calle El Progreso #2-5, Barrio El Pilar, Sonsonate',
    15, -- Asegúrate que el District con ID 15 exista (ej. El Congo)
    'sonsonate.progreso@miempresa.com.sv',
    TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP
),
(
    'Mini Sucursal La Libertad Puerto',
    '+503 2335-2040',
    'Calle Principal del Malecón, frente a muelle artesanal, Puerto de La Libertad',
    20, -- Asegúrate que el District con ID 20 exista (ej. Chalchuapa)
    'lalibertad.puerto@miempresa.com.sv',
    TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP
),
(
    'Agencia Chalatenango Centro',
    '+503 2301-7654',
    '4a Calle Poniente, Barrio El Centro, Chalatenango',
    25, -- Asegúrate que el District con ID 25 exista (ej. Nahulingo)
    'chalatenango.centro@miempresa.com.sv',
    TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP
),
(
    'Sucursal Usulután La Esperanza',
    '+503 2662-9012',
    'Barrio La Esperanza, 2a Avenida Norte, Usulután',
    30, -- Asegúrate que el District con ID 30 exista (ej. Armenia)
    'usulutan.esperanza@miempresa.com.sv',
    TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP
);

-- 3. VEHICLE CATEGORY
CREATE TABLE vehiclecategory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified_by VARCHAR(50),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 4. BRAND
CREATE TABLE brand (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified_by VARCHAR(50),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 5. MODEL
CREATE TABLE vehiclemodel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    brand_id INT,
    name VARCHAR(100),
    active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified_by VARCHAR(50),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (brand_id) REFERENCES brand(id)
);

-- 6. VEHICLE
CREATE TABLE vehicle (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plate VARCHAR(20),
    vehiclemodel_id INT,
    vehiclecategory_id INT,
    color VARCHAR(50),
    year YEAR,
    engine VARCHAR(100),
    engine_type VARCHAR(100),
    engine_number VARCHAR(100),
    vin VARCHAR(100),
    seat_count INT,
    description TEXT,
    status ENUM('Disponible', 'En mantenimiento', 'En reparacion', 'Reservado', 'Alquilado'),
    active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified_by VARCHAR(50),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehiclemodel_id) REFERENCES vehiclemodel(id),
    FOREIGN KEY (vehiclecategory_id) REFERENCES vehiclecategory(id)
);

CREATE TABLE vehicleimage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT,
    vehicle_image VARCHAR(255),
    FOREIGN KEY (vehicle_id) REFERENCES vehicle(id)
);

-- 1) Brands
INSERT INTO brand
   (name, active, created_by, created_at, modified_by, updated_at)
VALUES
  ('Toyota',    TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
  ('Ford',      TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
  ('Honda',     TRUE, 2, CURRENT_TIMESTAMP, 2, CURRENT_TIMESTAMP),
  ('BMW',       TRUE, 3, CURRENT_TIMESTAMP, 3, CURRENT_TIMESTAMP),
  ('Tesla',     TRUE, 4, CURRENT_TIMESTAMP, 4, CURRENT_TIMESTAMP);

-- 2) Vehicle Categories
INSERT INTO vehiclecategory
   (name, active, created_by, created_at, modified_by, updated_at)
VALUES
  ('Sedan',       TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
  ('SUV',         TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
  ('Hatchback',   TRUE, 2, CURRENT_TIMESTAMP, 2, CURRENT_TIMESTAMP),
  ('Coupe',       TRUE, 2, CURRENT_TIMESTAMP, 2, CURRENT_TIMESTAMP),
  ('Convertible', TRUE, 3, CURRENT_TIMESTAMP, 3, CURRENT_TIMESTAMP);

-- 3) Vehicle Models
INSERT INTO vehiclemodel
   (brand_id, name, active, created_by, created_at, modified_by, updated_at)
VALUES
  (1, 'Camry',    TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
  (1, 'Corolla',  TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
  (2, 'Focus',    TRUE, 2, CURRENT_TIMESTAMP, 2, CURRENT_TIMESTAMP),
  (2, 'Explorer', TRUE, 2, CURRENT_TIMESTAMP, 2, CURRENT_TIMESTAMP),
  (3, 'Civic',    TRUE, 3, CURRENT_TIMESTAMP, 3, CURRENT_TIMESTAMP);

-- 4) Vehicles
INSERT INTO vehicle
  (plate, vehiclemodel_id, vehiclecategory_id, color, year,
   engine, engine_type, engine_number, vin, seat_count, description,
   status, active, created_by, created_at, modified_by, updated_at)
VALUES
  ('ABC123', 1, 1, 'Blanco',   2020,
   '2.5L I4', 'Gasolina', 'ENG001', 'VIN001', 5, 'Sedán cómodo',
   'Disponible', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
  ('DEF456', 2, 1, 'Negro',    2019,
   '1.8L I4', 'Gasolina', 'ENG002', 'VIN002', 5, 'Sedán compacto',
   'Alquilado', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
  ('GHI789', 3, 3, 'Azul',     2021,
   '2.0L I4', 'Gasolina', 'ENG003', 'VIN003', 5, 'Hatchback ágil',
   'Reservado', TRUE, 2, CURRENT_TIMESTAMP, 2, CURRENT_TIMESTAMP),
  ('JKL012', 1, 2, 'Rojo',     2018,
   '3.0L V6', 'Diésel',   'ENG004', 'VIN004', 7, 'SUV familiar',
   'En mantenimiento', TRUE, 2, CURRENT_TIMESTAMP, 2, CURRENT_TIMESTAMP),
  ('MNO345', 2, 4, 'Plateado', 2022,
   'Motor Eléctrico', 'Eléctrico', 'ENG005', 'VIN005', 5, 'Coupé eléctrico',
   'En reparacion', TRUE, 3, CURRENT_TIMESTAMP, 3, CURRENT_TIMESTAMP);
   
INSERT INTO vehicle
  (plate, vehiclemodel_id, vehiclecategory_id, color, year,
   engine, engine_type, engine_number, vin, seat_count, description,
   status, active, created_by, created_at, modified_by, updated_at)
VALUES
  ('PQR678', 3, 4, 'Verde',    2017,
   '1.6L I4', 'Gasolina',           'ENG006', 'VIN006', 5, 'Compacto urbano',
   'En reparacion', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
  ('STU901', 2, 2, 'Gris',     2023,
   '4.0L V8', 'Gasolina',           'ENG007', 'VIN007', 2, 'Deportivo biplaza',
   'Disponible',   TRUE, 2, CURRENT_TIMESTAMP, 2, CURRENT_TIMESTAMP),
  ('VWX234', 1, 3, 'Amarillo',  2019,
   '2.2L I4 Turbo Diesel', 'Diésel','ENG008', 'VIN008', 5, 'Pick-up robusta',
   'Reservado',    TRUE, 3, CURRENT_TIMESTAMP, 3, CURRENT_TIMESTAMP),
  ('YZA567', 2, 4, 'Naranja',  2021,
   'Motor Híbrido',   'Híbrido', 'ENG009', 'VIN009', 5, 'Sedán híbrido',
   'Alquilado',    TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
  ('BCD890', 3, 1, 'Marrón',   2020,
   '3.5L V6', 'Gasolina',           'ENG010', 'VIN010', 7, 'SUV grande',
   'En mantenimiento', TRUE, 2, CURRENT_TIMESTAMP, 2, CURRENT_TIMESTAMP),
  ('EFG123', 1, 2, 'Azul Oscuro', 2022,
   'Gasolina/Eléctrico', 'Eléctrico','ENG011','VIN011', 5, 'Coche eléctrico',
   'Disponible',   TRUE, 3, CURRENT_TIMESTAMP, 3, CURRENT_TIMESTAMP),
  ('HIJ456', 2, 3, 'Blanco Perla', 2018,
   '2.0L I4 Turbo', 'Gasolina',     'ENG012','VIN012', 5, 'Hatchback deportivo',
   'Reservado',    TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
  ('KLM789', 3, 1, 'Negro Brillante', 2023,
   '1.2L I3', 'Gasolina',           'ENG013','VIN013', 4, 'Minivan',
   'Alquilado',    TRUE, 2, CURRENT_TIMESTAMP, 2, CURRENT_TIMESTAMP),
  ('NOP012', 1, 4, 'Rojo Vino',  2017,
   '2.5L I5', 'Híbrido',            'ENG014','VIN014', 8, 'Familiar espacioso',
   'En mantenimiento', TRUE, 3, CURRENT_TIMESTAMP, 3, CURRENT_TIMESTAMP),
  ('QRS345', 2, 3, 'Azul Cielo', 2021,
   '2.0L I4 Diésel', 'Diésel',      'ENG015','VIN015', 7, 'Todoterreno',
   'Disponible',   TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);


-- 5) Vehicle Images
INSERT INTO vehicleimage
  (vehicle_id, vehicle_image)
VALUES
  (1, 'https://example.com/img/veh1.jpg'),
  (2, 'https://example.com/img/veh2.jpg'),
  (3, 'https://example.com/img/veh3.jpg'),
  (4, 'https://example.com/img/veh4.jpg'),
  (5, 'https://example.com/img/veh5.jpg');




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