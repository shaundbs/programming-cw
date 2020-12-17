BEGIN TRANSACTION;

DROP TABLE IF EXISTS USERS;
DROP TABLE IF EXISTS APPOINTMENT;
DROP TABLE IF EXISTS DEPARTMENT;
DROP TABLE IF EXISTS PRESCRIPTION;
DROP TABLE IF EXISTS SPECIALISTS;
DROP TABLE IF EXISTS GP_TIME_OFF;
DROP TABLE IF EXISTS SLOTS;


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
	PRIMARY KEY("userId")
	-- UNIQUE("email") ?? 
);

CREATE TABLE IF NOT EXISTS "Appointment" (
	"startDate"	TEXT,
	"endDate"	TEXT,
	"is_confirmed"	INTEGER DEFAULT 0,
	"is_rejected"	INTEGER DEFAULT 0,
	"appointment_id"	INTEGER,
	"patient_id" INTEGER,
	"gp_id" INTEGER,
	PRIMARY KEY("appointment_id" AUTOINCREMENT),
	FOREIGN KEY("patient_id") REFERENCES Users(UserId),
	FOREIGN KEY("gp_id") REFERENCES Users(UserId)
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
	"surgery_name"	TEXT,
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
COMMIT;
