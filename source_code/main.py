import sys
import os
sys.path.append(os.getcwd()+'/patient_func')
sys.path.append(os.getcwd()+'/gp_func')

from patient_func.patients import Patient
from gp_func.gp import Gp
from patient_func.patient_database import Database
import bcrypt

db = Database()
# Welcome Page.
def welcome():
    print('Welcome')

def login():
    email = input('Email:')
    pWord = input('Password:')
    a = (email,)
    db.exec_one(
        "SELECT password, userId, accountType, is_registered FROM Users WHERE email = ?", a)
    record = db.c.fetchone()

    if not record:
        print('Sorry, your account does not exist in the system')
        login()

    elif bcrypt.checkpw(pWord.encode('utf-8'), record[0]):
        if record[2] == 'patient':
            if record[3] == 1:
                return ['patient', record[1]]
            else:
                print('Sorry, your registration is not approved yet.')
                return False
        elif record[2] == 'gp':
            return ['gp', record[1]]
        elif record[2] == 'admin':
            return ['admin', record[1]]

    else:
        print('Your password is wrong, Please retry.')
        login()

def user_options():
    print("1. Log in")
    print("2. Register")
    print("3. Exit")
    option = input("Enter your option : ")
    return option

def password_checker(pw):
    pass

welcome()

while True:
    # Display login/register.
    option = user_options()
    if option == "1":
        # Our patient want to log into the system.
        result = login()
        if result: # successful login
            if result[0] == 'gp':
                print('Log_in Successfull!')
                print(' ')
                gp = Gp(result[1])

            elif result[0] == 'patient':
                # Our patient successfully log in(after unlimited tries).
                print('Log_in Successfull!')
                print(' ')
                a = Patient(result[1])
                # Our patient is presented with available options.
                a.patient_home()

    elif option == "2":
        # Patient Register.
        Patient.register()

    elif option == "3":
        break

    else:
        print('Wrong input. Please try again.')
