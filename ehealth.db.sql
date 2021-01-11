BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Appointment" (
	"is_confirmed"	INTEGER DEFAULT 0,
	"is_rejected"	INTEGER DEFAULT 0,
	"appointment_id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"patient_id"	INTEGER,
	"gp_id"	INTEGER,
	"slot_id"	INTEGER,
	"reason"	TEXT DEFAULT 'None',
	"referred_specialist_id"	INTEGER,
	"clinical_notes"	TEXT,
	"is_completed"	INTEGER,
	FOREIGN KEY("referred_specialist_id") REFERENCES "Specialists"("specialist_id"),
	FOREIGN KEY("patient_id") REFERENCES "Users"("userId"),
	FOREIGN KEY("gp_id") REFERENCES "Users"("userId"),
	FOREIGN KEY("slot_id") REFERENCES "Slots"("slot_id")
);
CREATE TABLE IF NOT EXISTS "Prescription" (
	"medicine_name"	TEXT,
	"treatment_description"	TEXT,
	"pres_frequency_in_days"	NUMERIC,
	"startDate"	NUMERIC DEFAULT CURRENT_TIMESTAMP,
	"expiryDate"	NUMERIC,
	"prescription_id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"appointment_id"	INTEGER,
	FOREIGN KEY("appointment_id") REFERENCES "Appointment"("appointment_id")
);
CREATE TABLE IF NOT EXISTS "Department" (
	"name"	TEXT UNIQUE,
	"description"	TEXT,
	"department_id"	INTEGER PRIMARY KEY AUTOINCREMENT
);
CREATE TABLE IF NOT EXISTS "MedicalHistory" (
	"Medical_historyNo"	INTEGER,
	"UserID"	INTEGER,
	"illness"	TEXT,
	"time_afflicted"	TEXT,
	"description"	TEXT,
	"prescribed_medication"	TEXT,
	PRIMARY KEY("Medical_historyNo"),
	FOREIGN KEY("UserID") REFERENCES "Users"("userID")
);
CREATE TABLE IF NOT EXISTS "Slots" (
	"startTime"	NUMERIC,
	"endTime"	NUMERIC,
	"slot_id"	INTEGER,
	PRIMARY KEY("slot_id")
);
CREATE TABLE IF NOT EXISTS "Users" (
	"firstName"	TEXT,
	"lastName"	TEXT,
	"email"	TEXT UNIQUE,
	"password"	TEXT,
	"accountType"	TEXT,
	"is_registered"	INTEGER DEFAULT 0,
	"is_active"	INTEGER DEFAULT 0,
	"signUpDate"	NUMERIC,
	"userId"	INTEGER,
	"date_of_birth"	NUMERIC,
	PRIMARY KEY("userId")
);
CREATE TABLE IF NOT EXISTS "Specialists" (
	"firstName"	TEXT,
	"lastName"	TEXT,
	"hospital"	TEXT,
	"specialist_id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"department_id"	INTEGER,
	FOREIGN KEY("department_id") REFERENCES "Department"("department_id")
);
CREATE TABLE IF NOT EXISTS "gp_time_off" (
	"startTime"	NUMERIC,
	"endTime"	NUMERIC,
	"time_off_id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"gp_id"	INTEGER,
	FOREIGN KEY("gp_id") REFERENCES "Users"("userId")
);
COMMIT;
