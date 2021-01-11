import sqlite3
from os import system
import os
from time import sleep

from pandas import DataFrame
from tabulate import tabulate
from termcolor import colored

from .admin_email_generator import Emails
from . import admin_utilities as util
import logging


def clear():
    _ = os.system('cls' if os.name == 'nt' else 'clear')


def confirm_patient():
    """Allows admin to validate any patient accounts which have registered
    but have not been previously validated by an admin"""

    print(colored("\nPatients requiring validation:   ", 'blue', attrs=['bold']))

    try:
        connection = sqlite3.connect('database/ehealth.db')
        cursor = connection.cursor()

    except OperationalError:
        logging.exception("Database connection failure")
        print("Unable to connect to database!")

    # Query database for patients in need of validation
    query = """SELECT userID, firstName, lastName, email, signUpDate FROM Users WHERE is_registered = 0
             and accountType = 'patient' ORDER BY userID DESC"""
    cursor.execute(query)
    records = cursor.fetchall()

    global fullname_list
    fullname_list = []
    x = -1
    while x + 1 < len(records):
        x += 1
        fullname_list.append(records[x][1:3])

    df = DataFrame(records)
    index = ["ID", "First Name", "Last Name", "Email", "Date Signed Up"]
    try:
        df.columns = index
    except ValueError:
        logging.exception("Exception occurred whilst the patient pending_appt: ")
    clear()
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

    global validation_required
    global user_ids
    global emails
    validation_required = []
    user_ids = []
    emails = []
    for i in records:
        validation_required.append(i[1])
        user_ids.append(i[0])
        emails.append(i[3])
    if len(validation_required) == 0:
        print("\nThere are no patients currently requiring approval!")
        no_patients()

    connection.close()


def approve_all():
    patients_validated = []

    connection = sqlite3.connect('database/ehealth.db')
    cursor = connection.cursor()

    for i in range(len(validation_required)):
        cursor = connection.cursor()
        update_query = "UPDATE Users SET is_registered = ?, is_active = ?  WHERE userId = ?"
        data = (1, 1, user_ids[i])
        cursor.execute(update_query, data)
        connection.commit()
        patients_validated.append(validation_required[i])

    connection.close()
    print("All patients successfully approved!\n")
    util.loader("Sending confirmation emails")
    email = emails[i]
    firstName = fullname_list[i][0]
    lastName = fullname_list[i][1]

    Emails.validation_email(email, firstName, lastName, 'patient')
    clear()
    print(
        f"\nNumber of patients approved: {len(patients_validated)}")


def delete_all():
    patients_deleted = []

    connection = sqlite3.connect('database/ehealth.db')
    cursor = connection.cursor()

    for i in range(len(validation_required)):
        delete_query = "DELETE from Users WHERE userId = ?"
        delete_entry = user_ids[i]
        cursor.execute(delete_query, (delete_entry,))
        connection.commit()
        patients_deleted.append(validation_required[i])


    print("All patients successfully deleted!\n")
    util.loader('Loading')
    connection.close()
    clear()
    print(
        f"Number of patients deleted: {len(patients_deleted)}")


def validate():
    patients_validated = []
    patients_deleted = []

    connection = sqlite3.connect('database/ehealth.db')
    cursor = connection.cursor()

    # Loop through each patient and give user option to validate, delete or quit the program
    clear()
    for i in range(len(validation_required)):
        print(f"\n\nPatient ID: {user_ids[i]}\nPatient Name: {fullname_list[i][0]} {fullname_list[i][1]}")
        action1 = input("""Press enter to skip or choose one of the options below:
        \n1.Approve\n2.Delete\n3.Quit\nSelect option: """)
        if action1 == "1":
            cursor = connection.cursor()
            update_query = "UPDATE Users SET is_registered = ?, is_active = ?  WHERE userId = ?"
            data = (1, 1, user_ids[i])
            cursor.execute(update_query, data)
            connection.commit()
            print("Patient successfully approved!\n")
            patients_validated.append(validation_required[i])

            # Send user email confirming successful validation
            util.loader("Sending confirmation email")
            email = emails[i]
            firstName = fullname_list[i][0]
            lastName = fullname_list[i][1]

            Emails.validation_email(email, firstName, lastName, 'patient')

        elif action1 == "2":
            delete_query = "DELETE from Users WHERE userId = ?"
            delete_entry = user_ids[i]
            cursor.execute(delete_query, (delete_entry,))
            connection.commit()
            print("Patient successfully deleted!")
            patients_deleted.append(validation_required[i])

        elif action1 == "3":
            print("Exiting patient confirmation")
            break

        else:
            print("No action taken")
            pass

    connection.close()

    # Displays the total number of accounts validated/deleted
    util.loader('Loading')
    clear()
    print(
        f"\nNumber of patients approved: {len(patients_validated)}\nNumber of patients deleted: {len(patients_deleted)}")


def no_patients():
    util.loader('Loading')

