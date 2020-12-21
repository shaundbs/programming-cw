import sqlite3
from panel import Panel, Database
from patients import Patient
from gp import GP
from admin import Admin

# Welcome Page.
Panel().welcome()

while True:
    # Display login/register.
    option = Panel().user_options()
    if option == "1":
        # Our patient want to log into the system.
        result = Panel().login()
        if result:
            # Our patient successfully log in(after unlimited tries).
            print('Log_in Successfull!')
            print(' ')
            a = Patient(result[1])
            # Our patient is presented with available options.
            a.select_options()

    elif option == "2":
        # Patient Register.
        Patient.register()

    elif option == "3":
        break

    else:
        print('Wrong input. Please try again.')
