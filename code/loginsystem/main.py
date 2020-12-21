import sqlite3
from panel import Panel, Database
from patients import Patient
from gp import GP
from admin import Admin
from gp_func import gp

# Welcome Page.
Panel().welcome()

while True:
<<<<<<< HEAD
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
=======
    # Display available user modes.
    user_mode = Panel().homepage_options()

    if user_mode == "2":
        # Our user is a patient. He or she can choose to log in or register.
        option = Panel().patient_options()

        if option == "1":
            # Our patient want to log into the system.
            a = Patient()
            if a.log_in():
                # Our patient successfully log in(after unlimited tries).
                print('Log_in Successful!')
                print(' ')
                while True:
                    # Our patient is presented with available privileges.
                    privilege = a.select_options()
                    # TODO: design the privileges.
                    if privilege == '1':
                        a.request_appointment()
                    elif privilege == '2':
                        a.view_appointment()
                    elif privilege == '3':
                        a.cancel_appointment()
                    elif privilege == '4':
                        break
                    else:
                        print("Wrong input. Please try again.")

        elif option == "2":
            # Patient Register.
            Patient().register()

        else:
            print('Wrong input. Please try again.')

    elif user_mode == "1":
        # TODO
        print('Admin mode Not Available yet.')
        continue

    elif user_mode == "3":
        # TODO
        g = GP()
        print('GP mode Not Available yet.')
        continue

    elif user_mode == "4":
>>>>>>> c9fa140d5f703f5e90c4f894116558d9ed4a94d9
        break
    else:
        print('Wrong input. Please try again.')

# asdasdasdasasasd
