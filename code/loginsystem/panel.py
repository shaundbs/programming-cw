import sqlite3
from database import Database

# TODO: WHEN TO CLOSE DB?


class Panel:
    user_type = False
    user_id = 0

    def __init__(self):
        self.db = Database()

    def welcome(self):
        print('Welcome')

    def homepage_options(self):
        print("-----------------------------------------")
        print("|Enter 1 for Admin mode			|\n|Enter 2 for Patient mode	        |\n|Enter 3 for GP mode			|\n|Enter 4 Exit			        |")
        print("-----------------------------------------")
        Admin_user_mode = input("Enter your mode : ")
        return Admin_user_mode

    def patient_options(self):
        print("1. Log in")
        print("2. Register")
        option = input("Enter your option : ")
        return option

    def password_checker(self, pw):
        pass
