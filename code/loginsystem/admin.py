import sqlite3
import bcrypt
import getpass  # hide password when inputting
from database import Database


class Admin:
    login_status = False
    admin_id = 0

    def __init__(self):
        self.db = Database()

    def log_in(self):
        pass

    def select_options(self):
        pass

    def confirm_registration(self):
        pass

    def add_gp(self):
        pass

    def manage_gp(self):
        pass

    def manage_records(self):
        pass

   

########T

from panel import Panel, Database
import pandas as pd
from pd import DataFrame



def select_options(self):
    print('1. Search Patient')
    print('2. Search GP')
    print('3. Register GP')
    print('4. Approve Patient')
    option = input('Please choose an option: ')
    return option


def SearchDoB(self):
    DoB = input("Enter Date of Birth: ")
    db = Database()
    Index= ["First Name", "Last Name", "DateOfBirth", "email", "Role", "Registered", "Active", "Signed UP", "ID"]
    db.exec_one("SELECT FirstName, LastName, DateOfBirth, email, accountType, is_registered, is_active, signUpDate, userID  FROM Users WHERE DateOfBirth = ?", (DoB,))
    result = db.c.fetchall()
    df = DataFrame(result)
    df.columns = Index
    print(df)
    return df

def SearchByName(self):
    FirstName = input("First Name: ")
    LastName = input("Last Name: ")
    db = Database()
    Index= ["First Name", "Last Name", "DateOfBirth", "email", "Role", "Registered", "Active", "Signed UP", "ID"]
    db.exec_one("SELECT FirstName, LastName, DateOfBirth, email, accountType, is_registered, is_active, signUpDate, userID  FROM Users WHERE FirstName = ? and LastName=?", (FirstName,LastName,))
    result = db.c.fetchall()
    df = DataFrame(result)
    df.columns = Index
    print(df)
    return df




def SeePatientRecord(self,userid,df):
    pass


def DeletePatientRecord(self):
    pass


def DeactivatePatient(self):
    pass





