import sqlite3
from panel import Panel
from patients import Patient
# from gp import GP
from admin import Admin
from gp_func import Gp

# Welcome Page.
Panel().welcome()

while True:
    # Display login/register.
    option = Panel().user_options()
    if option == "1":
        # Our patient want to log into the system.
        result = Panel().login()
        print(result)

        if result[0] == 'gp':
            user = Gp(result[1])
            user.print_welcome()
            user.main_options() # call initial function for main menu state to begin state management.

        elif result[0] == 'patient':
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
        break
    else:
        print('Wrong input. Please try again.')

# asdasdasdasasasd
