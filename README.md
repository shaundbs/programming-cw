# programming-cw
## Database Schema:
1. Appointment 
   - "slot_id"	INTEGER,
   - "is_confirmed"	INTEGER DEFAULT 0,
   - "is_rejected"	INTEGER DEFAULT 0,
   - "appointment_id"	INTEGER,
   - "patient_id"	INTEGER,
   - "gp_id"	INTEGER,
   - **"reason"	TEXT,**
   - **"referred_specialist_id"	INTEGER,**
   - **"clinical_notes"	TEXT,**
   - **"is_completed"	INTEGER,**
(data from patient team)

2. Users
    - "firstName"	TEXT,
    - "lastName"	TEXT,
	- "email"	TEXT,
	- "password"	TEXT,
	- "accountType"	TEXT,
	- "is_registered"	INTEGER,
	- "is_active"	INTEGER,
	- "signUpDate"	TEXT DEFAULT CURRENT_TIMESTAMP,(**format**)
	- "userId"	INTEGER,
	- **"date_of_birth"	TEXT,**
(data from all teams)

3. slots
   - "slot_id"	INTEGER,
   - "startTime"	TEXT,
   - "endTime"	TEXT,
(data in 2021 year that **excludes weekend**)

4. specialist
    - "firstName"	TEXT,
    - "lastName"	TEXT,
    - "**hospital**"	TEXT,
    - "specialist_id"	INTEGER,
    - "department_id"	INTEGER,
(data from gp team)

5. Department
    - "name"	INTEGER,
    - "description"	INTEGER,
    - "department_id"	INTEGER
(data from gp team)

6. gp_time_off
    - "time_off_id"	INTEGER,
    - "gp_id"	INTEGER,
    - "startTime"	TEXT,
    - "endTime"	TEXT
(data from gp team)

7. **Prescription**
    - "medicine_name"	TEXT,
    - "treatment_description"	TEXT,
    - "pres_frequency_in_days"	NUMERIC,
    - "startDate"	TEXT DEFAULT CURRENT_TIMESTAMP,
    - "expiryDate"	TEXT,
    - "prescription_id"	INTEGER,
    - "appointment_id"	INTEGER
(data from gp team)

8. **MedicalHistory**
	- "Medical_historyNo"	INTEGER,
	- "UserID"	INTEGER,
	- "illness"	TEXT,
	- "time_afflicted"	TEXT,
	- "description"	TEXT,
	- "prescribed_medication"	TEXT
 (data from admin team)
 
## Resources:
### [SQLLITE3:](https://docs.python.org/3/library/sqlite3.html)
1. https://stackoverflow.com/questions/6318126/why-do-you-need-to-create-a-cursor-when-querying-a-sqlite-database
2. To **retrieve data** after executing a SELECT statement, you can either treat the cursor as an **iterator**, call the cursor’s **fetchone()** method to retrieve a single matching row, or call **fetchall()** to get a list of the matching rows.
3. Usually your SQL operations will need to use values from Python variables. You shouldn’t assemble your query using Python’s string operations because doing so is insecure; it makes your program vulnerable to an SQL injection attack (see https://xkcd.com/327/ for humorous example of what can go wrong).
- Instead, use the DB-API’s parameter substitution. Put **?** as a placeholder wherever you want to use a value, and then provide a **tuple** of values as the second argument to the cursor’s execute() method. (Other database modules may use a different placeholder, such as %s or :1.)
### [Bcrypt:](http://zetcode.com/python/bcrypt/)
1. encode before use: line.encode('utf-8'), 
1. salt = **bcrypt.gensalt()**; hashed = **bcrypt.hashpw(passwd, salt)**; if **bcrypt.checkpw(passwd, hashed)**:
### [Tkinter:](https://www.youtube.com/watch?v=YXPyB4XeYLA&feature=youtu.be)
