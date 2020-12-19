import sqlite3
import bcrypt
import getpass  # hide password when inputting
from database import Database
import re
<<<<<<< HEAD
import datetime as datetime
=======
>>>>>>> parent of 94c19df... Update login system


class Patient:
    patient_id = 0
    login_status = False
    registration_status = False

    def __init__(self):
        self.db = Database()

    def register(self):
        # Register. User input.
        # TODO: data validation.
<<<<<<< HEAD
        fName = input('First Name:')
=======
        fName = input('Fist Name:')
>>>>>>> parent of 94c19df... Update login system
        lName = input('Last Name:')


        email_repetition = True
        email_list = Database().patient_email_list()

        while email_repetition:
            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
            email = input('Email:')
            if not re.search(regex, email):
                print("Invalid Email. Please try again.")
            elif email not in email_list:
                email_repetition = False
                break
            else:
                print('This email has been registered. Please try again')

        pWord = getpass.getpass('Password:')

        # Encode pw and insert user credentials into db.
        pWord = pWord.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pWord, salt)
<<<<<<< HEAD
        aType = "patient"
        time_now = datetime.datetime.now()
        date_time = time_now.strftime("%m/%d/%Y %H:%M:%S")
        a = [(fName, lName, email, hashed, aType, date_time, ), ]
        self.db.exec_many(
            "INSERT INTO Users(firstName,lastName,email,password,accountType,signUpDate) Values (?,?,?,?,?,?)", a)
=======
        a = [(fName, lName, email, hashed), ]
        self.db.exec_many(
            "INSERT INTO Patients(firstName,lastName,email,password) Values (?,?,?,?)", a)

>>>>>>> parent of 94c19df... Update login system
    def log_in(self):
        email = input('Email:')
        pWord = getpass.getpass('Password:')
        a = (email,)
        self.db.exec_one(
<<<<<<< HEAD
            "SELECT password, userId, valid_status FROM Users WHERE email = ?", a)
=======
            "SELECT password, userId, valid_status FROM Patients WHERE email = ?", a)
>>>>>>> parent of 94c19df... Update login system
        record = self.db.c.fetchone()
        pWord = pWord.encode('utf-8')

        if not record:
            print('Sorry, your account does not exist in the system')
            self.log_in()

<<<<<<< HEAD
        elif bcrypt.checkpw(pWord, record[0]):  
=======
        elif bcrypt.checkpw(pWord, record[0]):
>>>>>>> parent of 94c19df... Update login system
            if record[2] == 1:
                self.patient_id = record[1]
                self.login_status = True
                return True
            else:
                print('Sorry, your registration is not approved yet.')
                return False

        else:
            print('Your password is wrong, Please retry.')
            self.log_in()

    def select_options(self):
        print('1. Request Appointments')
        print('2. View Appointments')
        print('3. Cancel Appointments')
        print('4. Log out')
        option = input('Please choose an option: ')
        return option

    def request_appointment(self):
        if self.login_status:
            print("Patient id: " + str(self.patient_id) +
                  " request appointment\n")
            return

    def view_appointment(self):
        if self.login_status:
            print("Patient id: " + str(self.patient_id) +
                  "want to view appointment\n")
            return

    def cancel_appointment(self):
        if self.login_status:
            print("Patient id: " + str(self.patient_id) +
                  "want to cancel appointment\n")
            return
