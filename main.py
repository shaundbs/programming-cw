import logging
import sys
import os
import re

from admin_func.admin import Admin
from patient_func.patients import Patient
from gp_func.gp import Gp
from patient_func.patient_database import Database
import bcrypt
import cli_ui as ui

# disable colours for windows compatibility
if os.name == 'nt':
    ui.setup(color='never')


# Welcome Page.
def welcome():
    ui.info_section(
        "Welcome to University College Hospital(UCH) - Online System.\n\nTel: 020 3456 7890\nAddress: University "
        "College Hospital, 235 Euston Road, London, NW1 2BU.")
    ui.info("* For testing purpose only:")
    ui.info("- Patient Email: patient@test.com")
    ui.info("- GP Email: gp@test.com")
    ui.info("- Admin Email: admin@test.com")
    ui.info("- Password(for all above): Persona123\n")

class Panel:
    def __init__(self):
        self.db = Database()
        # self.tries = 0
        self.userType = None
        self.userId = None

    def login(self):
        while True:
            email = ui.ask_string("Please input your registered email:")
            p_word = ui.ask_password('Please input your password:')
            a = (email,)
            self.db.exec_one(
                "SELECT password, userId, accountType, is_registered, is_active FROM Users WHERE email = ?", a)
            record = self.db.c.fetchone()

            if record and bcrypt.checkpw(p_word.encode('utf-8'), record[0]):
                if record[-1] == 0:
                    ui.info('Sorry, your account is being deactivated for now.')
                    break
                if record[2] == 'patient':
                    if record[3] == 1:
                        self.userType = 'patient'
                        self.userId = record[1]
                    else:
                        ui.info('Sorry, your registration is not approved yet.')
                elif record[2] == 'gp':
                    self.userType = 'gp'
                    self.userId = record[1]
                elif record[2] == 'admin':
                    self.userType = 'admin'
                    self.userId = record[1]
                break
            else:
                if not record:
                    ui.info('Sorry, we could not find your account in the system. Please double check your input.')
                else:
                    ui.info('Sorry, your password is not correct.')
                retry_login = ui.ask_yes_no("Would you like to try again?", default=False)
                if not retry_login:
                    ui.info('You have exited from the system')
                    break

    def enter_system(self):
        if self.userType == 'patient':
            Patient(self.userId).patient_home()
        elif self.userType == 'gp':
            Gp(self.userId)
        elif self.userType == 'admin':
            Admin(self.userId)


if __name__ == '__main__':
    # initialise logging file
    logging.basicConfig(filename='e_patient_system.log', filemode='a', format='%(asctime)s - %(levelname)s - %('
                                                                              'message)s')
try:
    # Main loop.
    while True:
        newPanel = Panel()
        welcome()
        registerStatus = ui.ask_yes_no("Do you already have an account?", default=False)
        if registerStatus:
            newPanel.login()
            if newPanel.userType:
                newPanel.enter_system()
        else:
            toRegister = ui.ask_yes_no("Do you want to register a new account?", default=False)
            if toRegister:
                Patient.register()
        toExit = ui.ask_yes_no("Do you want to exit the system?", default=False)
        if toExit:
            ui.info('You have exited from the system.')
            break
except KeyboardInterrupt:
    ui.info(" Keyboard Interrupt detected - Exiting application...")
