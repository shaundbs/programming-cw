import datetime
import re
from os import system
import threading
import bcrypt
from .admin_database import Database
from .admin_email_generator import Emails
from . import admin_utilities as util


def clear():
    _ = os.system('cls' if os.name == 'nt' else 'clear')


def registerGP():
    """Allows user logged in with admin privileges to register
    a new account for a GP"""

    clear()
    print("Registration form for new GPs \n")

    # First name validation
    first_ver = True
    global firstName
    while first_ver:

        firstName = input("First Name: ")
        if firstName == '9':
            Admin().admin_options()

        elif firstName.isalpha():
            firstName = firstName.title()
            first_ver = False
        else:
            print("Invalid input")
            first_ver = True

    # Second name validation
    last_ver = True
    global lastName
    while last_ver:

        lastName = input("Last Name: ")
        if lastName.isalpha():
            lastName = lastName.title()
            last_ver = False
        else:
            print("Invalid input")
            last_ver = True

    # Email validation
    email_list = Database().email_list()
    email_repetition = True

    global email
    while email_repetition:
        regex = '^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$'

        email = input('Email: ')
        if not re.search(regex, email):
            print("Invalid Email. Please try again.")
        elif email not in email_list:
            email = email.lower()
            email_repetition = False
            break
        else:
            print("This email address has already been registered. Please try again.")

    # Set password
    pass_val = True
    global pWord
    while pass_val:

        pWord = input("Password: ")
        if len(pWord) < 5:
            print("Password must be at least 5 characters")
        else:
            pass_val = False

    clear()
    # Display summary of account details
    print("\nSummary of GP details: ")
    print(f"Name: Dr {firstName} {lastName}\nEmail: {email}\nPassword: {pWord}\n")


def confirmation():

    curr_date = datetime.datetime.now()
    format_date = curr_date.strftime("%m-%d-%Y %H:%M")

    # Encode password and insert user credentials into db
    passWord = pWord.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(passWord, salt)
    a = [(firstName, lastName, email, hashed, 'gp','1','1',format_date), ]
    try:
        Database().exec_many(
            """INSERT INTO Users(firstName,lastName,email,password,accountType,is_registered,is_active,signUpDate)
             Values (?,?,?,?,?,?,?,?)""", a)
    except OperationalError:
        logging.exception("Error adding GP details to database")
        clear()
        print("Registration unsuccessful")
        ver1 = True
        while ver1:

            inp = input("1.Try again\n2.Return to the main menu\nSelect option: ")
            if inp == "1":
                clear()
                ver1 = False
                registerGP()
            elif inp == "2":
                ver1 = False
                clear()
                print("Program Terminated")
                Database().connection.close()
                sys.exit()
            else:
                clear()
                print("Please select a valid option!")

    else:
        clear()

        # Display summary of account details
        print("Registration successful!\n")

        # Email new user with the relevant details
        try:
            util.loader("Sending confirmation email")
            Emails.gp_registration_email(email, firstName, lastName, pWord, 'GP')
            print("\nEmail has been sent with a record of the account details\n")
        except UnboundLocalError:
            logging.exception("Exception occurred while trying to send confirmation of GP registration email")
            print("\nSorry, unable to send email...\n")


if __name__ == "__main__":
    registerGP()