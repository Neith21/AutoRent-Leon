-- ¡¡¡ IMPORTANTE, PRIMERO CREAR LA BD Y LUEGO HACER LAS MIGRACIONES !!! --
CREATE DATABASE IF NOT EXISTS autorentleon;
USE autorentleon;

-- ¡¡¡ LUEGO DE HACER LAS MIGRACIONES PROCEDER A INSERTAR SÓLO SI YA SE CREÓ UN SUPERUSUARIO !!! --
INSERT INTO users_metadata (user_id, user_image) VALUES (1, 'hola_mundo.jpg');

INSERT INTO department (code, department, active, created_by, created_at, modified_by, updated_at) VALUES
('01', 'Ahuachapán', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('02', 'Santa Ana', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('03', 'Sonsonate', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('04', 'Chalatenango', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('05', 'La Libertad', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('06', 'San Salvador', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('07', 'Cuscatlán', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('08', 'La Paz', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('09', 'Cabañas', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('10', 'San Vicente', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('11', 'Usulután', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('12', 'San Miguel', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('13', 'Morazán', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('14', 'La Unión', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);

INSERT INTO municipality (code, municipality, department_id, active, created_by, created_at, modified_by, updated_at) VALUES
('0101', 'Ahuachapán Centro', 1, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0102', 'Ahuachapán Norte', 1, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0103', 'Ahuachapán Sur', 1, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0201', 'Santa Ana Centro', 2, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0202', 'Santa Ana Este', 2, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0203', 'Santa Ana Norte', 2, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0204', 'Santa Ana Oeste', 2, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0301', 'Sonsonate Centro', 3, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0302', 'Sonsonate Este', 3, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0303', 'Sonsonate Norte', 3, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0304', 'Sonsonate Oeste', 3, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0401', 'Chalatenango Centro', 4, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0402', 'Chalatenango Norte', 4, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0403', 'Chalatenango Sur', 4, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0501', 'La Libertad Centro', 5, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0502', 'La Libertad Costa', 5, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0503', 'La Libertad Este', 5, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0504', 'La Libertad Norte', 5, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0505', 'La Libertad Oeste', 5, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0506', 'La Libertad Sur', 5, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0601', 'San Salvador Centro', 6, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0602', 'San Salvador Este', 6, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0603', 'San Salvador Norte', 6, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0604', 'San Salvador Oeste', 6, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0605', 'San Salvador Sur', 6, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0701', 'Cuscatlán Norte', 7, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0702', 'Cuscatlán Sur', 7, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0801', 'La Paz Centro', 8, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0802', 'La Paz Este', 8, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0803', 'La Paz Oeste', 8, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0901', 'Cabañas Este', 9, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('0902', 'Cabañas Oeste', 9, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('1001', 'San Vicente Norte', 10, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('1002', 'San Vicente Sur', 10, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('1101', 'Usulután Este', 11, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('1102', 'Usulután Norte', 11, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('1103', 'Usulután Oeste', 11, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('1201', 'San Miguel Centro', 12, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('1202', 'San Miguel Norte', 12, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('1203', 'San Miguel Oeste', 12, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('1301', 'Morazán Norte', 13, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('1302', 'Morazán Sur', 13, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('1401', 'La Unión Norte', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('1402', 'La Unión Sur', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);

INSERT INTO district (code, district, municipality_id, active, created_by, created_at, modified_by, updated_at) VALUES
('10101', 'Ahuachapán', 1, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('10102', 'Apaneca', 1, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('10104', 'Concepción de Ataco', 1, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('10111', 'Tacuba', 1, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('10203', 'Atiquizaya', 2, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('10205', 'El Refugio', 2, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('10209', 'San Lorenzo', 2, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('10212', 'Turín', 2, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('10306', 'Guaymango', 3, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('10307', 'Jujutla', 3, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('10308', 'San Francisco Menéndez', 3, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('10310', 'San Pedro Puxtla', 3, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('20110', 'Santa Ana', 4, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('20202', 'Coatepeque', 5, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('20204', 'El Congo', 5, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('20306', 'Masahuat', 6, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('20307', 'Metapán', 6, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('20311', 'Santa Rosa Guachipilín', 6, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('20313', 'Texistepeque', 6, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('20401', 'Candelaria de la Frontera', 7, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('20403', 'Chalchuapa', 7, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('20405', 'El Porvenir', 7, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('20408', 'San Antonio Pajonal', 7, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('20409', 'San Sebastián Salitrillo', 7, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('20412', 'Santiago de la Frontera', 7, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('30109', 'Nahulingo', 8, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('30111', 'San Antonio del Monte', 8, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('30114', 'Santo Domingo de Guzmán', 8, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('30115', 'Sonsonate', 8, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('30116', 'Sonzacate', 8, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('30202', 'Armenia', 9, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('30203', 'Caluco', 9, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('30204', 'Cuisnahuat', 9, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('30205', 'Santa Isabel Ishuatán', 9, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('30206', 'Izalco', 9, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('30212', 'San Julián', 9, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('30307', 'Juayúa', 10, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('30308', 'Nahuizalco', 10, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('30310', 'Salcoatitán', 10, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('30313', 'Santa Catarina Masahuat', 10, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('30401', 'Acajutla', 11, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40101', 'Agua Caliente', 12, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40108', 'Dulce Nombre de María', 12, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40110', 'El Paraíso', 12, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40113', 'La Reina', 12, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40116', 'Nueva Concepción', 12, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40122', 'San Fernando', 12, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40124', 'San Francisco Morazán', 12, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40131', 'San Rafael', 12, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40132', 'Santa Rita', 12, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40133', 'Tejutla', 12, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40204', 'Citalá', 13, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40225', 'San Ignacio', 13, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40212', 'La Palma', 13, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40302', 'Arcatao', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40303', 'Azacualpa', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40305', 'Comalapa', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40306', 'Concepción Quezaltepeque', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40307', 'Chalatenango', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40309', 'El Carrizal', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40311', 'La Laguna', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40314', 'Las Vueltas', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40315', 'Nombre de Jesús', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40317', 'Nueva Trinidad', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40318', 'Ojos de Agua', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40319', 'Potonico', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40320', 'San Antonio de la Cruz', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40321', 'San Antonio Los Ranchos', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40326', 'San Isidro Labrador', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40323', 'San Francisco Lempa', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40327', 'San José Cancasque / Cancasque', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40328', 'San José Las Flores / Las Flores', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40329', 'San Luis del Carmen', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('40330', 'San Miguel de Mercedes', 14, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50102', 'Ciudad Arce', 15, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50115', 'San Juan Opico', 15, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50205', 'Chiltiupán', 16, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50208', 'Jicalapa', 16, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50209', 'La Libertad', 16, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50218', 'Tamanique', 16, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50220', 'Teotepeque', 16, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50301', 'Antiguo Cuscatlán', 17, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50306', 'Huizúcar', 17, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50310', 'Nuevo Cuscatlán', 17, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50314', 'San José Villanueva', 17, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50322', 'Zaragoza', 17, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50412', 'Quezaltepeque', 18, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50416', 'San Matías', 18, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50417', 'San Pablo Tacachico', 18, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50503', 'Colón', 19, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50507', 'Jayaque', 19, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50513', 'Sacacoyo', 19, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50519', 'Talnique', 19, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50521', 'Tepecoyo', 19, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50604', 'Comasagua', 20, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('50611', 'Santa Tecla antes: Nueva San Salvador', 20, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('60103', 'Ayutuxtepeque', 21, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('60104', 'Cuscatancingo', 21, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('60108', 'Mejicanos', 21, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('60114', 'San Salvador', 21, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('60119', 'Delgado', 21, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('60207', 'Ilopango', 22, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('60213', 'San Martín', 22, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('60217', 'Soyapango', 22, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('60218', 'Tonacatepeque', 22, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('60301', 'Aguilares', 23, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('60305', 'El Paisnal', 23, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('60306', 'Guazapa', 23, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('60402', 'Apopa', 24, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('60409', 'Nejapa', 24, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('60510', 'Panchimalco', 25, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('60511', 'Rosario de Mora', 25, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('60512', 'San Marcos', 25, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('60515', 'Santiago Texacuangos', 25, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('60516', 'Santo Tomás', 25, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('70106', 'Oratorio de Concepción', 26, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('70107', 'San Bartolomé Perulapía', 26, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('70109', 'San José Guayabal', 26, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('70110', 'San Pedro Perulapán', 26, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('70115', 'Suchitoto', 26, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('70201', 'Candelaria', 27, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('70202', 'Cojutepeque', 27, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('70203', 'El Carmen', 27, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('70204', 'El Rosario', 27, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('70205', 'Monte San Juan', 27, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('70208', 'San Cristóbal', 27, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('70211', 'San Rafael Cedros', 27, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('70212', 'San Ramón', 27, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('70213', 'Santa Cruz Analquito', 27, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('70214', 'Santa Cruz Michapa', 27, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('70216', 'Tenancingo', 27, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80102', 'El Rosario / Rosario de La Paz', 28, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80103', 'Jerusalén', 28, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80104', 'Mercedes La Ceiba', 28, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80106', 'Paraíso de Osorio', 28, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80107', 'San Antonio Masahuat', 28, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80108', 'San Emigdio', 28, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80112', 'San Juan Tepezontes', 28, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80114', 'San Miguel Tepezontes', 28, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80116', 'San Pedro Nonualco', 28, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80118', 'Santa María Ostuma', 28, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80119', 'Santiago Nonualco', 28, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80122', 'San Luis La Herradura', 28, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80210', 'San Juan Nonualco', 29, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80217', 'San Rafael Obrajuelo', 29, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80221', 'Zacatecoluca', 29, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80301', 'Cuyultitán', 30, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80305', 'Olocuilta', 30, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80309', 'San Francisco Chinameca', 30, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80311', 'San Juan Talpa', 30, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80313', 'San Luis Talpa', 30, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80315', 'San Pedro Masahuat', 30, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('80320', 'Tapalhuaca', 30, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('90109', 'Dolores / Villa Dolores', 31, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('90102', 'Guacotecti', 31, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('90105', 'San Isidro', 31, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('90106', 'Sensuntepeque', 31, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('90108', 'Victoria', 31, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('90201', 'Cinquera', 32, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('90203', 'Ilobasco', 32, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('90204', 'Jutiapa', 32, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('90207', 'Tejutepeque', 32, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('100101', 'Apastepeque', 33, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('100106', 'San Esteban Catarina', 33, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('100107', 'San Ildefonso', 33, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('100108', 'San Lorenzo', 33, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('100109', 'San Sebastián', 33, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('100104', 'Santa Clara', 33, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('100105', 'Santo Domingo', 33, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('100202', 'Guadalupe', 34, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('100203', 'San Cayetano Istepeque', 34, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('100210', 'San Vicente', 34, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('100211', 'Tecoluca', 34, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('100212', 'Tepetitán', 34, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('100213', 'Verapaz', 34, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110103', 'California', 35, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110104', 'Concepción Batres', 35, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110106', 'Ereguayquín', 35, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110110', 'Jucuarán', 35, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110113', 'Ozatlán', 35, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110123', 'Usulután', 35, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110117', 'San Dionisio', 35, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110118', 'Santa Elena', 35, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110120', 'Santa María', 35, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110122', 'Tecapán', 35, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110201', 'Alegría', 36, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110202', 'Berlín', 36, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110205', 'El Triunfo', 36, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110207', 'Estanzuelas', 36, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110209', 'Jucuapa', 36, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110211', 'Mercedes Umaña', 36, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110212', 'Nueva Granada', 36, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110216', 'San Buenaventura', 36, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110221', 'Santiago de María', 36, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110308', 'Jiquilisco', 37, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110314', 'Puerto El Triunfo', 37, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110315', 'San Agustín', 37, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('110319', 'San Francisco Javier', 37, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120103', 'Comacarán', 38, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120109', 'Moncagua', 38, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120106', 'Chirilagua', 38, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120112', 'Quelepa', 38, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120117', 'San Miguel', 38, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120120', 'Uluazapa', 38, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120201', 'Carolina', 39, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120202', 'Ciudad Barrios', 39, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120204', 'Chapeltique', 39, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120211', 'Nuevo Edén de San Juan', 39, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120213', 'San Antonio del Mosco', 39, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120214', 'San Gerardo', 39, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120216', 'San Luis de La Reina', 39, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120219', 'Sesori', 39, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120305', 'Chinameca', 40, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120307', 'El Tránsito', 40, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120308', 'Lolotique', 40, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120310', 'Nueva Guadalupe', 40, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120315', 'San Jorge', 40, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('120318', 'San Rafael Oriente', 40, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130101', 'Arambala', 41, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130102', 'Cacaopera', 41, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130103', 'Corinto', 41, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130107', 'El Rosario', 41, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130110', 'Joateca', 41, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130111', 'Jocoaitique', 41, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130114', 'Meanguera', 41, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130116', 'Perquín', 41, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130118', 'San Fernando', 41, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130120', 'San Isidro', 41, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130124', 'Torola', 41, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130204', 'Chilanga', 42, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130205', 'Delicias de Concepción', 42, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130206', 'El Divisadero', 42, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130208', 'Gualococti', 42, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130209', 'Guatajiagua', 42, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130212', 'Jocoro', 42, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130213', 'Lolotiquillo', 42, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130215', 'Osicala', 42, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130217', 'San Carlos', 42, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130219', 'San Francisco Gotera', 42, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130221', 'San Simón', 42, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130222', 'Sensembra', 42, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130223', 'Sociedad', 42, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130225', 'Yamabal', 42, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('130226', 'Yoloaiquín', 42, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('140101', 'Anamorós', 43, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('140102', 'Bolívar', 43, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('140103', 'Concepción de Oriente', 43, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('140106', 'El Sauce', 43, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('140109', 'Lislique', 43, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('140111', 'Nueva Esparta', 43, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('140112', 'Pasaquina', 43, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('140113', 'Polorós', 43, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('140115', 'San José La Fuente', 43, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('140116', 'Santa Rosa de Lima', 43, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('140204', 'Conchagua', 44, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('140205', 'El Carmen', 44, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('140207', 'Intipucá', 44, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('140208', 'La Unión', 44, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('140210', 'Meanguera del Golfo', 44, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('140214', 'San Alejo', 44, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('140217', 'Yayantique', 44, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('140218', 'Yucuaiquín', 44, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);

INSERT INTO branch (name, phone, address, district_id, email, active, created_by, created_at, modified_by, updated_at) VALUES
('Sucursal Central Apopa', '+503 2215-1020', 'Avenida Quirino Chávez #45, Barrio El Centro, Apopa, San Salvador', 1, 'central.apopa@miempresa.com.sv', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Agencia Santa Tecla Las Delicias', '+503 2228-4578', 'Centro Comercial Las Delicias, Local 12B, Carretera Panamericana, Santa Tecla, La Libertad', 5, 's.tecla.delicias@miempresa.com.sv', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Punto de Venta San Miguel Roosevelt', '+503 2661-3399', 'Avenida Roosevelt Sur, Edificio Comercial La Confianza, San Miguel', 10, 'sanmiguel.roosevelt@miempresa.com.sv', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Oficina Sonsonate El Progreso', '+503 2451-8870', 'Calle El Progreso #2-5, Barrio El Pilar, Sonsonate', 15, 'sonsonate.progreso@miempresa.com.sv', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Mini Sucursal La Libertad Puerto', '+503 2335-2040', 'Calle Principal del Malecón, frente a muelle artesanal, Puerto de La Libertad', 20, 'lalibertad.puerto@miempresa.com.sv', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Agencia Chalatenango Centro', '+503 2301-7654', '4a Calle Poniente, Barrio El Centro, Chalatenango', 25, 'chalatenango.centro@miempresa.com.sv', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Sucursal Usulután La Esperanza', '+503 2662-9012', 'Barrio La Esperanza, 2a Avenida Norte, Usulután', 30, 'usulutan.esperanza@miempresa.com.sv', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);

INSERT INTO brand (name, active, created_by, created_at, modified_by, updated_at) VALUES
('Toyota',    TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Ford',      TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Honda',     TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('BMW',       TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Tesla',     TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);

INSERT INTO vehiclecategory (name, active, created_by, created_at, modified_by, updated_at) VALUES
('Sedan',       TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('SUV',         TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Hatchback',   TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Coupe',       TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Convertible', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);

INSERT INTO vehiclemodel (brand_id, name, active, created_by, created_at, modified_by, updated_at) VALUES
(1, 'Camry',    TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(1, 'Corolla',  TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(2, 'Focus',    TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(2, 'Explorer', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(3, 'Civic',    TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);

INSERT INTO vehicle (plate, vehiclemodel_id, vehiclecategory_id, branch_id, color, year, engine, engine_type, engine_number, vin, seat_count, daily_price, description, status, active, created_by, created_at, modified_by, updated_at) VALUES
('ABC123X', 1, 1, 1, 'Rojo Cereza', 2023, '2.5L I4', 'Gasolina', 'ENG100001', '1HGCM82P9JA123450', 5, 55.00, 'Toyota Camry Sedan familiar', 'Disponible', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('DEF456Y', 2, 3, 2, 'Azul Profundo', 2022, '1.8L I4', 'Gasolina', 'ENG100002', 'SALVD23R7KB543210', 5, 48.50, 'Toyota Corolla Hatchback deportivo', 'Alquilado', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('GHI789Z', 3, 3, 3, 'Blanco Nacarado', 2024, 'Motor Electrico 150kW', 'Electrico', 'ENG100003E', '3FA6P0H7XRJ198765', 5, 52.00, 'Ford Focus Electrico Hatchback', 'Reservado', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('JKL012A', 4, 2, 4, 'Gris Oxford', 2021, '2.3L Ecoboost', 'Gasolina', 'ENG100004D', 'JN1AZ48G7LW234567', 7, 70.00, 'Ford Explorer SUV espacioso', 'En mantenimiento', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('MNO345B', 5, 1, 5, 'Negro Onix', 2023, '1.5L Turbo Hibrido', 'Hibrido', 'ENG100005H', '2T1BURHE7NC456789', 5, 58.00, 'Honda Civic Sedan hibrido eficiente', 'Disponible', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('PQR678C', 2, 1, 6, 'Verde Esmeralda', 2020, '1.8L I4', 'Gasolina', 'ENG100006', 'WVWZZZ1KZLW098765', 5, 45.00, 'Toyota Corolla Sedan compacto', 'En reparacion', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('STU901D', 1, 1, 7, 'Plata Lunar', 2024, '2.5L I4', 'Gasolina', 'ENG100007', '1N4AL3AP4DN654321', 5, 60.00, 'Toyota Camry Sedan elegante', 'Disponible', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('VWX234E', 4, 2, 1, 'Amarillo Solar', 2022, 'Motor Electrico Dual', 'Electrico', 'ENG100008E', '5YJSA1E2XPF789012', 7, 75.50, 'Ford Explorer SUV electrico', 'Alquilado', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('YZA567F', 2, 1, 2, 'Naranja Vibrante', 2021, '1.6L GLP', 'GLP', 'ENG100009L', 'KM8SR43A2MU876543', 5, 47.00, 'Toyota Corolla Sedan con GLP', 'Reservado',TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('BCD890G', 4, 2, 3, 'Marron Tabaco', 2020, '3.0L V6 Diesel', 'Diesel', 'ENG100010D', 'WMXGZ2J7XLD765432', 7, 72.00, 'Ford Explorer SUV Diesel robusta', 'Disponible', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('EFG123H', 1, 1, 4, 'Azul Zafiro', 2023, '2.5L Hibrido', 'Hibrido', 'ENG100011', 'TRUAB7C53NH123987', 5, 59.50, 'Toyota Camry Sedan hibrido', 'En mantenimiento', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('HIJ456J', 5, 1, 5, 'Rojo Pasion', 2022, '2.0L Hibrido Enchufable', 'Hibrido', 'ENG100012H', 'YV1BW78H2M1092345', 5, 57.00, 'Honda Civic Sedan hibrido enchufable', 'Disponible', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('KLM789K', 3, 3, 6, 'Gris Titanio', 2024, 'Motor Electrico 100kW', 'Electrico', 'ENG100013E', '4JGDA5EBXGE567123', 4, 53.00, 'Ford Focus Electrico Hatchback compacto', 'Alquilado', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('NOP012L', 4, 2, 7, 'Blanco Alpino', 2021, '2.2L Diesel', 'Diesel', 'ENG100014D', 'VF15R4HX4PJ234901', 7, 73.50, 'Ford Explorer SUV Diesel', 'Reservado', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('QRS345M', 5, 3, 1, 'Negro Cosmos', 2023, '1.5L Turbo', 'Gasolina', 'ENG100015', 'ZFA2500000J345678', 5, 50.00, 'Honda Civic Hatchback moderno', 'Disponible', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);

INSERT INTO vehicleimage (vehicle_id, vehicle_image) VALUES
(1, '1.png'),
(2, '2.png'),
(3, '3.png'),
(4, '4.png'),
(5, '5.png'),
(6, '2.png'),
(7, '1.png'),
(8, '4.png'),
(9, '2.png'),
(10, '4.png'),
(11, '1.png'),
(12, '5.png'),
(13, '3.png'),
(14, '4.png'),
(15, '5.png');

/* INSERT INTO customer (first_name, last_name, document_type, document_number, address, phone, email, customer_type, birth_date, status, reference, notes, active, created_by, created_at, modified_by, updated_at) VALUES
('Juan Carlos', 'Pérez Gómez', 'DUI', '12345678-9', 'Colonia San Benito, Calle La Mascota, #52, San Salvador', '78554321', 'juan.perez@email.com', 'Nacional', '1990-05-15', 'Activo', 'Ana Martínez - 7766-5544', 'Cliente referido por la sucursal de Santa Tecla.', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);

INSERT INTO rental (customer_id, vehicle_id, pickup_branch_id, return_branch_id, start_date, end_date, actual_return_date, status, total_price, fuel_level_pickup, fuel_level_return, remarks, active, created_by, created_at, modified_by, updated_at)
VALUES (
    1, -- ID del cliente Juan Carlos Pérez Gómez
    1, -- ID del vehículo 'ABC123X' (Toyota Camry)
    1, -- ID de la sucursal de recogida
    1, -- ID de la sucursal de devolución
    '2025-06-07 10:00:00', -- Fecha de inicio del alquiler
    '2025-06-10 10:00:00', -- Fecha de finalización del alquiler
    NULL, -- Aún no se ha devuelto
    'Activo', -- El alquiler está en curso
    165.00, -- Precio calculado (55.00/día * 3 días)
    'Lleno', -- Nivel de combustible al recoger
    NULL, -- Aún no se ha devuelto
    'Se verificó la llanta de repuesto y las herramientas. El cliente pagó un anticipo.',
    TRUE,
    1,
    CURRENT_TIMESTAMP,
    1,
    CURRENT_TIMESTAMP
); */

-- ==================================================
-- 1. Inserción de Clientes
-- ==================================================

-- Cliente 1: Nacional
INSERT INTO customer (id, first_name, last_name, document_type, document_number, address, phone, email, customer_type, birth_date, status, notes, active, created_by, created_at, modified_by, updated_at) VALUES
(1, 'Juan', 'Pérez', 'DUI', '01234567-8', 'Calle Falsa 123, San Salvador', '7888-9999', 'juan.perez@email.com', 'Nacional', '1990-05-15', 'Activo', 'Cliente recurrente, sucursal principal.', TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP);

-- Cliente 2: Extranjero
INSERT INTO customer (id, first_name, last_name, document_type, document_number, address, phone, email, customer_type, birth_date, status, notes, active, created_by, created_at, modified_by, updated_at) VALUES
(2, 'John', 'Smith', 'Pasaporte', 'A1B23C456', '456 Oak Avenue, New York', '555-1234', 'john.smith@email.com', 'Extranjero', '1985-10-20', 'Activo', 'Primera vez que alquila. Se verificó pasaporte y licencia internacional.', TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP);


-- ==================================================
-- 2. Alquileres ACTIVOS para Cliente 1 (Juan Pérez, ID=1)
-- ==================================================

-- Alquiler 1: Activo, corta duración (4 días), requiere pago parcial 50%.
INSERT INTO rental (id, customer_id, vehicle_id, pickup_branch_id, return_branch_id, start_date, end_date, actual_return_date, status, total_price, fuel_level_pickup, fuel_level_return, remarks, active, created_by, created_at, modified_by, updated_at) VALUES 
(1, 1, 1, 1, 1, '2025-06-08 10:00:00', '2025-06-12 10:00:00', NULL, 'Activo', 220.00, 'Lleno', NULL, 'Anticipo del 50% recibido. Vehículo entregado sin detalles.', TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP);

-- Pago de anticipo para el alquiler 1
INSERT INTO payment (rental_id, amount, payment_type, payment_date, concept, reference, active, created_by, created_at, modified_by, updated_at) VALUES
(1, 110.00, 'Tarjeta de Credito', '2025-06-08 10:05:00', 'Anticipo', '', TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP);

-- Alquiler 2: Activo, larga duración (10 días), requiere pago total.
INSERT INTO rental (id, customer_id, vehicle_id, pickup_branch_id, return_branch_id, start_date, end_date, actual_return_date, status, total_price, fuel_level_pickup, fuel_level_return, remarks, active, created_by, created_at, modified_by, updated_at) VALUES
(2, 1, 2, 1, 2, '2025-06-09 14:00:00', '2025-06-19 14:00:00', NULL, 'Activo', 500.00, '1/2', NULL, 'Pago total recibido por ser más de 5 días de alquiler.', TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP);

-- Pago total (considerado anticipo) para el alquiler 2
INSERT INTO payment (rental_id, amount, payment_type, payment_date, concept, reference, active, created_by, created_at, modified_by, updated_at) VALUES
(2, 500.00, 'Efectivo', '2025-06-09 14:05:00', 'Anticipo', '', TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP);


-- ==================================================
-- 3. Alquiler FINALIZADO para Cliente 2 (John Smith, ID=2)
-- ==================================================

-- Alquiler 3: Finalizado
INSERT INTO rental (id, customer_id, vehicle_id, pickup_branch_id, return_branch_id, start_date, end_date, actual_return_date, status, total_price, fuel_level_pickup, fuel_level_return, remarks, active, created_by, created_at, modified_by, updated_at) VALUES
(3, 2, 3, 2, 2, '2025-05-20 09:00:00', '2025-05-23 09:00:00', '2025-05-23 08:45:00', 'Finalizado', 180.00, 'Lleno', 'Lleno', 'Vehículo devuelto en excelentes condiciones. Se procede a reembolsar depósito.', TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP);

-- Pagos para el alquiler 3.
INSERT INTO payment (rental_id, amount, payment_type, payment_date, concept, reference, active, created_by, created_at, modified_by, updated_at) VALUES
(3, 100.00, 'Tarjeta de Credito', '2025-05-20 09:05:00', 'Anticipo', 'Cargo extra, gasolina', TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(3, 100.00, 'Tarjeta de Credito', '2025-05-20 09:05:00', 'Anticipo', 'Depósito de seguridad para extranjero', TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(3, 90.00, 'Tarjeta de Credito', '2025-05-20 09:05:00', 'Anticipo', '50% del costo del alquiler', TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(3, 90.00, 'Tarjeta de Credito', '2025-05-23 08:50:00', 'Pago Final', 'Pago del 50% restante', TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP),
(3, -100.00, 'Tarjeta de Credito', '2025-05-23 08:55:00', 'Reembolso', 'Devolución de depósito de seguridad', TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP);

-- Factura generada para el alquiler 3 (pagada)
INSERT INTO invoice (rental_id, invoice_number, issue_date, total_amount, reference, status, active, created_by, created_at, modified_by, updated_at) VALUES
(3, 'INV-2025-0001', '2025-05-23 09:00:00', 180.00, 'Hola', 'Pagada', TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP);

-- ==================================================
-- 4. Alquiler ACTIVO para Cliente 2 (John Smith, ID=2)
-- ==================================================

INSERT INTO rental (id, customer_id, vehicle_id, pickup_branch_id, return_branch_id, start_date, end_date, actual_return_date, status, total_price, fuel_level_pickup, fuel_level_return, remarks, active, created_by, created_at, modified_by, updated_at) VALUES 
(4, 2, 1, 1, 1, '2025-06-09 10:00:00', '2025-06-13 10:00:00', NULL, 'Activo', 220.00, 'Lleno', NULL, 'Anticipo del 50% recibido. Vehículo entregado sin detalles.', TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP);

-- Pago de anticipo para el alquiler 1
INSERT INTO payment (rental_id, amount, payment_type, payment_date, concept, reference, active, created_by, created_at, modified_by, updated_at) VALUES
(4, 110.00, 'Tarjeta de Credito', '2025-06-09 10:05:00', 'Anticipo', '', TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP);

INSERT INTO payment (rental_id, amount, payment_type, payment_date, concept, reference, active, created_by, created_at, modified_by, updated_at) VALUES
(4, 100.00, 'Tarjeta de Credito', '2025-06-09 10:05:00', 'Depósito', '', TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP);


INSERT INTO company (trade_name, nrc, classification, phone, address, logo, email, website, active, created_by, created_at, modified_by, updated_at, logo_lqip, logo_public_id) VALUES
('AutoRent León', '123426-7', 'Mediana', '+50322554433', 'Calle La Mascota, #550, San Vicente', 'https://res.cloudinary.com/dmu3idwnm/image/upload/v1749607522/company_logos/ksudrewxhxbubdtvxbne.jpg', 'contacto1@autorentleon.com', 'https://www.autorentleon.com', TRUE, '1', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP, 'https://res.cloudinary.com/dmu3idwnm/image/upload/w_200/e_blur:100/q_auto:low/v1749607522/company_logos/ksudrewxhxbubdtvxbne.jpg', 'company_logos/ksudrewxhxbubdtvxbne');