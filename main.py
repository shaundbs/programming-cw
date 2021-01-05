import sys
import os
import re
sys.path.append(os.getcwd()+'/patient_func')
sys.path.append(os.getcwd()+'/gp_func')
sys.path.append(os.getcwd()+'/admin_func')

from admin_func.admin import Admin
from patient_func.patients import Patient
from gp_func.gp import Gp
from patient_func.patient_database import Database
import bcrypt
import cli_ui as ui


# Welcome Page.
class Panel:
    def __init__(self):
        self.db = Database()
        # self.tries = 0
        self.userType = None
        self.userId = None

    def welcome(self):
        ui.info_section("Welcome to University College Hospital(UCH) - Online System.\n\nTel: 020 3456 7890\nAddress: University College Hospital, 235 Euston Road, London, NW1 2BU.")

    def login(self):
        email = ui.ask_string("Please input your registered email:")
        pWord = ui.ask_password('Please input your password:')
        a = (email,)
        self.db.exec_one(
            "SELECT password, userId, accountType, is_registered FROM Users WHERE email = ?", a)
        record = self.db.c.fetchone()

        if record and bcrypt.checkpw(pWord.encode('utf-8'), record[0]):
            if record[2] == 'patient':
                if record[3] == 1:
                    self.userType = 'patient'
                    self.userId = record[1]
                else:
                    ui.info('Sorry, your registration is not approved yet.')
                    return False
            elif record[2] == 'gp':
                self.userType = 'gp'
                self.userId = record[1]
            elif record[2] == 'admin':
                self.userType = 'admin'
                self.userId = record[1]
            return True
        else:
            if not record:
                ui.info('Sorry, we could not find your account in the system. Please double check your input.')
            else:
                ui.info('Sorry, your password is not correct.')
            retryLogin = ui.ask_yes_no("Do you want to have another try?", default=False)
            if retryLogin:
                self.login()
            else:
                return False

    def enterSystem(self):
        if self.userType == 'patient':
            Patient(self.userId).patient_home()
        elif self.userType == 'gp':
            Gp(self.userId)
        elif self.userType == 'admin':
            Admin(self.userId)

# Main loop.
while True:
    newPanel = Panel()
    newPanel.welcome()
    registerStatus = ui.ask_yes_no("Do you already have an account?", default=False)
    if registerStatus:
        loginResult = newPanel.login()
        if loginResult:
            newPanel.enterSystem()
            toExit = ui.ask_yes_no("Do you want to exit the system?", default=False)
            if toExit:
                break
    else:
        toRegister = ui.ask_yes_no("Do you want to register a new account?", default=False)
        if toRegister:
            Patient.register()
        else:
            break
