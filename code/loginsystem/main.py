import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from patient_func.patients import Patient
from panel import Panel

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
            a.patient_home()

    elif option == "2":
        # Patient Register.
        Patient.register()

    elif option == "3":
        break

    else:
        print('Wrong input. Please try again.')
