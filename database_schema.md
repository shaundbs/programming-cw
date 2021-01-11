# programming-cw
## Database Schema:
1. Appointment (data from patient team)
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

2. Users (data from all teams)
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

3. slots (data in 2021 year that **excludes weekend**)
   - "slot_id"	INTEGER,
   - "startTime"	TEXT,
   - "endTime"	TEXT,

4. specialist (data from gp team)
    - "firstName"	TEXT,
    - "lastName"	TEXT,
    - "**hospital**"	TEXT,
    - "specialist_id"	INTEGER,
    - "department_id"	INTEGER,

5. Department (data from gp team)
    - "name"	INTEGER,
    - "description"	INTEGER,
    - "department_id"	INTEGER

6. gp_time_off (data from gp team)
    - "time_off_id"	INTEGER,
    - "gp_id"	INTEGER,
    - "startTime"	TEXT,
    - "endTime"	TEXT

7. **Prescription** (data from gp team)
    - "medicine_name"	TEXT,
    - "treatment_description"	TEXT,
    - "pres_frequency_in_days"	NUMERIC,
    - "startDate"	TEXT DEFAULT CURRENT_TIMESTAMP,
    - "expiryDate"	TEXT,
    - "prescription_id"	INTEGER,
    - "appointment_id"	INTEGER

8. **MedicalHistory** (data from admin team)
	- "Medical_historyNo"	INTEGER,
	- "UserID"	INTEGER,
	- "illness"	TEXT,
	- "time_afflicted"	TEXT,
	- "description"	TEXT,
	- "prescribed_medication"	TEXT
 
## Resources:
### [SQLLITE3:](https://docs.python.org/3/library/sqlite3.html)
1. https://stackoverflow.com/questions/6318126/why-do-you-need-to-create-a-cursor-when-querying-a-sqlite-database
2. To **retrieve data** after executing a SELECT statement, you can either treat the cursor as an **iterator**, call the cursor’s **fetchone()** method to retrieve a single matching row, or call **fetchall()** to get a list of the matching rows.
3. Usually your SQL operations will need to use values from Python variables. You shouldn’t assemble your query using Python’s string operations because doing so is insecure; it makes your program vulnerable to an SQL injection attack (see https://xkcd.com/327/ for humorous example of what can go wrong).
- Instead, use the DB-API’s parameter substitution. Put **?** as a placeholder wherever you want to use a value, and then provide a **tuple** of values as the second argument to the cursor’s execute() method. (Other database modules may use a different placeholder, such as %s or :1.)
### [Bcrypt:](http://zetcode.com/python/bcrypt/)
1. encode before use: line.encode('utf-8'), 
1. salt = **bcrypt.gensalt()**; hashed = **bcrypt.hashpw(passwd, salt)**; if **bcrypt.checkpw(passwd, hashed)**:

