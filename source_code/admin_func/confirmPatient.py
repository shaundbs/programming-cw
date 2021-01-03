import sqlite3
from admin_database import Database
import smtplib, ssl
from pandas import DataFrame
import os
from os import system
from tabulate import tabulate
from termcolor import colored
from time import sleep
from email_generator import Emails



def clear():
    _ = system('clear')

def confirmPatient():
    """Allows admin to validate any patient accounts which have registered
    but have not been previously validated by an admin"""

    print(colored("\nPatients requiring validation:   ", 'blue', attrs=['bold']))


    connection = sqlite3.connect('../../database/ehealth.db')
    cursor = connection.cursor()

    # Query database for patients in need of validation
    query = "SELECT userID, firstName, lastName, email, signUpDate FROM Users WHERE is_registered = 0 and accountType = 'patient'"
    cursor.execute(query)
    records = cursor.fetchall()



    global fullname_list
    fullname_list = []
    x=-1
    while x+1 < len(records):
        x+=1
        fullname_list.append(records[x][1:3])


    df = DataFrame(records)
    index = ["ID", "First Name", "Last Name", "Email", "Date Signed Up"]
    df.columns = index
    print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))

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
        print("\nThere are no patients currently requiring validation!")

        no_patients()

    connection.close()




def validate():

    patients_validated = []
    patients_deleted = []

    connection = sqlite3.connect('/Users/anna/Desktop/66CW/database/ehealth.db')
    cursor = connection.cursor()

    # Loop through each patient and give user option to validate, delete or quit the program
    for i in range(len(validation_required)):
        print("\nPatient Name:",validation_required[i])
        action1 = input("1.Validate\n2.Delete\n3.Quit\nSelect option: ")
        if action1 == "1":
            cursor = connection.cursor()
            update_query = "UPDATE Users SET is_registered = ?, is_active = ?  WHERE userId = ?"
            data = (1, 1, user_ids[i])
            cursor.execute(update_query, data)
            connection.commit()
            print("Patient successfully validated!\n")
            patients_validated.append(validation_required[i])

            #Send user email confirming successful validation
            email = emails[i]
            firstName = fullname_list[i][0]
            lastName = fullname_list[i][1]



            Emails.validation_email(email, firstName, lastName, 'patient')



        elif action1 == "2":
            delete_query = "DELETE from Users WHERE userId = ?"
            delete_entry = user_ids[i]
            cursor.execute(delete_query, (delete_entry, ))
            connection.commit()
            print("Patient successfully deleted!\n")
            patients_deleted.append(validation_required[i])

        elif action1 == "3":
            print("Program Terminated")
            break

        else:
            print("No action taken\n")
            pass

    connection.close()

    # Displays the total number of accounts validated/deleted
    sleep(1)
    clear()
    print(f"Number of patients validated: {len(patients_validated)}\nNumber of patients deleted: {len(patients_deleted)}")

def no_patients():
    sleep(1)





if __name__ == "__main__":
    confirmPatient()