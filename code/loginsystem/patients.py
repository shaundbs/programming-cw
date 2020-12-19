import sqlite3
# hide password when inputting
from database import Database
import re
import bcrypt
import getpass


class Patient:
    patient_id = 0

    def __init__(self, id):
        self.patient_id = id

    @classmethod
    def register(cls):
        # Register. User input.
        # TODO: data validation.
        db = Database()
        fName = input('Fist Name:')
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
        a = [(fName, lName, email, hashed, 'patient'), ]
        db.exec_many(
            "INSERT INTO Users(firstName,lastName,email,password,accountType) Values (?,?,?,?,?)", a)

    def select_options(self):
        print('1. Request Appointments')
        print('2. View Appointments')
        print('3. View Prescription')
        print('4. Log out')
        option = input('Please choose an option: ')
        return option

    def request_appointment(self):
        pass

    def view_appointment(self):
        a = [(self.patient_id), ]
        db = Database()
        db.exec_one("SELECT * FROM Appointment WHERE patient_Id = ?", a)
        result = db.c.fetchall()
        for i in result:
            print(i)

    def view_prescription(self):
        print("Patient id: " + str(self.patient_id) +
              "want to view prescription\n")
        return


if __name__ == "__main__":
    Patient(1).view_appointment()
