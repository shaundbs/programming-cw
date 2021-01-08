BEGIN TRANSACTION;
--
--DROP TABLE IF EXISTS USERS;
--DROP TABLE IF EXISTS APPOINTMENT;
--DROP TABLE IF EXISTS DEPARTMENT;
--DROP TABLE IF EXISTS PRESCRIPTION;
--DROP TABLE IF EXISTS SPECIALISTS;
--DROP TABLE IF EXISTS GP_TIME_OFF;
--DROP TABLE IF EXISTS SLOTS;


CREATE TABLE IF NOT EXISTS "Users" (
	"firstName"	TEXT,
	"lastName"	TEXT,
	"email"	TEXT,
	"password"	TEXT,
	"accountType"	TEXT,
	"is_registered"	INTEGER,
	"is_active"	INTEGER,
	"signUpDate" TEXT DEFAULT CURRENT_TIMESTAMP,
	"userId"	INTEGER,
	"date_of_birth" TEXT,
	PRIMARY KEY("userId" AUTOINCREMENT)
	-- UNIQUE("email") ?? 
);

CREATE TABLE IF NOT EXISTS "Appointment" (
	"slot_id" INTEGER,
	"is_confirmed"	INTEGER DEFAULT 0,
	"is_rejected"	INTEGER DEFAULT 0,
	"appointment_id"	INTEGER,
	"patient_id" INTEGER,
	"gp_id" INTEGER,
	"reason" TEXT,
	"referred_specialist_id" INTEGER,
	"clinical_notes" TEXT,
	"is_completed" INTEGER,
	PRIMARY KEY("appointment_id" AUTOINCREMENT),
	FOREIGN KEY("patient_id") REFERENCES Users(UserId),
	FOREIGN KEY("gp_id") REFERENCES Users(UserId),
    FOREIGN KEY("slot_id") REFERENCES slots(slot_id)
	FOREIGN KEY("referred_specialist_id") REFERENCES Specialists(specialist_id)
);

CREATE TABLE IF NOT EXISTS "slots" (
	"slot_id" INTEGER,
	"startTime" TEXT,
	"endTime" TEXT,
	PRIMARY KEY("slot_id" AUTOINCREMENT),
	UNIQUE("startTime")
);

CREATE TABLE IF NOT EXISTS "gp_time_off" (
	"time_off_id" INTEGER,
	"gp_id" INTEGER,
	"startTime" TEXT,
	"endTime" TEXT,
	PRIMARY KEY("time_off_id" AUTOINCREMENT),
	FOREIGN KEY("gp_id") REFERENCES Users(UserId)
);

CREATE TABLE IF NOT EXISTS "Prescription" (
	"medicine_name"	TEXT,
	"treatment_description"	TEXT,
	"pres_frequency_in_days"	NUMERIC,
	"startDate" TEXT DEFAULT CURRENT_TIMESTAMP,
	"expiryDate"	TEXT,
	"prescription_id"	INTEGER,
	"appointment_id"	INTEGER,
	PRIMARY KEY("prescription_id" AUTOINCREMENT),
	FOREIGN KEY("appointment_id") REFERENCES Appointment(appointment_id)
);

CREATE TABLE IF NOT EXISTS "Department" (
	"name"	INTEGER,
	"description"	INTEGER,
	"department_id"	INTEGER,
	PRIMARY KEY("department_id" AUTOINCREMENT),
	UNIQUE("name")
);

CREATE TABLE IF NOT EXISTS "Specialists" (
	"firstName"	TEXT,
	"lastName"	TEXT,
	"hospital"	TEXT,
	"specialist_id"	INTEGER,
	"department_id" INTEGER,
	PRIMARY KEY("specialist_id" AUTOINCREMENT),
	FOREIGN KEY("department_id") REFERENCES Department(department_id)
);


-- INSERT INTO "Users" VALUES ('y','z','$2b$12$./wMwdXovKEp9orquJIVluAwqPH51IhivgIaCM6DXigaPFv4ruYge',1,NULL,0);
-- INSERT INTO "Users" VALUES ('na','la','$2b$12$83ch9Qc1Fm4Q4mEVWwCXIuCRWL7x55bC7afxuyAxbYYkI4zradDLG',2,NULL,0);
-- INSERT INTO "Users" VALUES ('a','b','$2b$12$GL0WE9L9JePMUnhQOMjRG.of9W4H/n4qVl13.AqVTwHwQk1SbWZ.6',3,NULL,0);
-- INSERT INTO "Users" VALUES ('a','b','$2b$12$5d8Xo5rudnXjCjCOczChEOrYWOSH8ItweB0SiIOn18RITAHbl7M8i',4,NULL,0);
-- INSERT INTO "Users" VALUES ('y','z','$2b$12$.tsNkhEzGWvZIm9/SAuQIudA.Q8Ik9k6gePudB4ZXTCerW7NqRRWq',5,NULL,0);
-- INSERT INTO "Users" VALUES ('Y','Z','$2b$12$H.QCOpRJqUhPGENBP86.Nu2YTl25f8y4WM5AnzoKWlZYYFjkyvsGG',6,NULL,0);
-- INSERT INTO "Users" VALUES ('y','z','$2b$12$S15czMDpRyJr4CSp4jrQC.Lw7nY6fc8j9MINLTEAj1KdeO4nJIjRy',7,NULL,0);
-- INSERT INTO "Users" VALUES ('yang','zou','$2b$12$UfqJUqjyziwFYWtK8KkfsOhEKk4OBzbyyBB3hhGhManyDZcJGdYcy',8,NULL,0);
-- INSERT INTO "Users" VALUES ('ha','ha','$2b$12$teh.tUJPtwDHCqgqGYaf7OVr.QjoW1LY5oxcObNryctPw.C3IKZnC',9,'2284@qq.com',1);
-- INSERT INTO "Users" VALUES ('ya','zo','$2b$12$FbnaZ/h1JqJDxsq0ypk.YeRRnNtbfEsXGo4sFzhMoK1IcC8ksKEgG',10,'2284@qq.com',0);
-- INSERT INTO "Users" VALUES ('ya','zo','$2b$12$MlMIGEXx5TwD7ZrVdzunJOzf8xQnT78s28IopWVi9t2Wwdfnumgp.',11,'2284@qq.com',0);
-- INSERT INTO "Users" VALUES ('ya','za','$2b$12$pep2I.WAA75p6UQQmiZa3.c3Sgx5oUVtw7CO7jbhXi8i62MyK/.ki',12,'2284@qq.com',0);
-- INSERT INTO "Users" VALUES ('ya','zo','$2b$12$zsv0jcpelhrWOZA//kQLJeTVLzlHC0p42kDQ/s3IGyoYBdvidPW7y',13,'2284@qq.com',0);
-- INSERT INTO "Users" VALUES ('ya','zo','$2b$12$mgS0vhOry889Z3BGQOgivOkaQX54yQWoI4gWpaO.IUIKdwrZY2dsa',14,'2284@qq.com',0);
-- INSERT INTO "Users" VALUES ('ya','zo','$2b$12$3qowQC3i9II7EMCkxKntCONOjLGKMITiEaCZlMXd3EpLYIF/HbETm',15,'2284@qq.com',0);
-- INSERT INTO "Users" VALUES ('uu','aa','$2b$12$xmlFCtlvzVZhyh.le63zX.Gr6uhMAxrXyfA3qupH5tRdid.PgTaCC',16,'2285@qq.com',0);
-- INSERT INTO "Users" VALUES ('nh','ya','$2b$12$lztUEfcj1NWlydnJEL9RYe14kaPleanTkpiQ2I0tjNYE40.c6Xvqi',17,'2886@qq.com',1);

-- admin test user, password: test
--INSERT INTO USERS(FIRSTNAME, LASTNAME, EMAIL, PASSWORD, ACCOUNTTYPE, IS_ACTIVE) VALUES ('admin', 'test', 'admin@test.com','$2y$12$RtLSd8p2ODkGdfw9K3/IduYm3drd0KrJerNSBoYYj5tTc5Cw.msvK', 'admin', 1);

--INSERT INTO USERS(FIRSTNAME, LASTNAME, EMAIL, PASSWORD, ACCOUNTTYPE) VALUES ('Qasim', 'Razvi', 'qr@test.com','$2b$12$oAJxmL.Pa9Y7.U20pvqZ2ef65.8ls3.9U/S2EhZO7ewFo7mHUSihu', 'gp');
--
--INSERT INTO DEPARTMENT (NAME)
--VALUES
--('Anaesthetics'),
--('Ear nose and throat (ENT)'),
--('Diagnostic imaging'),
--('General surgery'),
--('Maternity (antenatal)'),
--('Cardiology'),
--('Breast screening')
--;
--
--INSERT INTO SPECIALISTS (FIRSTNAME, LASTNAME, HOSPITAL, DEPARTMENT_ID)
--VALUES
--('Simon','Barnett','London Hospital',1),
--('Tylar','Ainsworth','Birmingham Hospital',2),
--('Pru','Beck','Manchester Hospital',3),
--('Graeme','Danielson','Leeds Hospital',4),
--('Shawnee','Spence','Newcastle Hospital',5),
--('Addison','Peck','Birstall Hospital',6),
--('Bysshe','Kingston','Glasgow Hospital',7),
--('Moti','Averill','Liverpool Hospital',1),
--('Natalie','Sommer','Portsmouth Hospital',2),
--('Byrne','Winchester','Southampton Hospital',3),
--('Livvy','Neal','Nottingham Hospital',4),
--('Cissy','Alamilla','Bristol Hospital',5),
--('Antonia','Park','Sheffield Hospital',6),
--('Wilfrid','Dickson','Kingston upon Hull Hospital',7),
--('Gaz','Vega','Leicester Hospital',1),
--('Clementine','Fonseca','Edinburgh Hospital',2),
--('Safaa','Eliott','Caerdydd Hospital',3),
--('Kyla','Millard','Stoke-on-Trent Hospital',4),
--('Olujimi','Garrod','Coventry Hospital',5),
--('Yousef','Teel','Reading Hospital',6),
--('Gust','Van Amelsvoort','Belfast Hospital',7),
--('Janina','Meeuwes','Derby Hospital',1),
--('Helge','Tangeman','Plymouth Hospital',2),
--('Carla','Grosse','Wolverhampton Hospital',3),
--('Auguste','Porto','Abertawe Hospital',4),
--('Masao','De Wit','Milton Keynes Hospital',5),
--('Viviette','Owston','Aberdeen Hospital',6),
--('Helmine','Fujioka','Norwich Hospital',7),
--('Leoluca','Alberda','London Hospital',1),
--('Michael','Ryer','Birmingham Hospital',2),
--('Auguste','Fonseca','Manchester Hospital',3),
--('Masao','Eliott','Leeds Hospital',4),
--('Hadewych','Millard','Newcastle Hospital',5),
--('Helmine','Garrod','Birstall Hospital',6),
--('Leoluca','Teel','Glasgow Hospital',7),
--('Graeme','Van Amelsvoort','Liverpool Hospital',1),
--('Shawnee','Meeuwes','Portsmouth Hospital',2),
--('Addison','Tangeman','Southampton Hospital',3),
--('Bysshe','Grosse','Nottingham Hospital',4),
--('Moti','Porto','Bristol Hospital',5),
--('Natalie','Danielson','Sheffield Hospital',6),
--('Byrne','Spence','Kingston upon Hull Hospital',7),
--('Livvy','Peck','Leicester Hospital',1),
--('Rafael','Kingston','Edinburgh Hospital',2),
--('Antonia','Averill','Caerdydd Hospital',3),
--('Wilfrid','Sommer','Stoke-on-Trent Hospital',4),
--('Gaz','Winchester','Coventry Hospital',5),
--('Clementine','Neal','Reading Hospital',6),
--('John','Alamilla','Belfast Hospital',7),
--('Safaa','Park','Derby Hospital',1),
--('Kyla','Dickson','Plymouth Hospital',2),
--('Olujimi','Dayson','Wolverhampton Hospital',3),
--('Chelsea','Penny','Abertawe Hospital',4),
--('Carla','Stamp','Milton Keynes Hospital',5),
--('Ethelyn','Waters','Aberdeen Hospital',6),
--('Jena','Day','Norwich Hospital',7);

COMMIT;
