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
            while True:
                a = Patient(result[1])
                # Our patient is presented with available privileges.
                privilege = a.select_options()
                # TODO: design the privileges.
                if privilege == '1':
                    booked_slot = a.request_time()
                    if booked_slot < '0':
                        a.request_appointment()
                elif privilege == '2':
                    a.view_appointment()
                elif privilege == '3':
                    a.view_prescription()
                elif privilege == '4':
                    break
                else:
                    print("Wrong input. Please try again.")

    elif option == "2":
        # Patient Register.
        Patient.register()
    elif option == "3":
        break
    else:
        print('Wrong input. Please try again.')