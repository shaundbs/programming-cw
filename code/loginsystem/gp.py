import sqlite3
import bcrypt
import getpass  # hide password when inputting
from database import Database


class GP:
    gp_id = 0
    login_status = False
    account_status = True

    def __init__(self):
        self.db = Database()

    def log_in(self):
        pass

    def select_options(self):
        pass

    def add_availability(self):
        pass

    def manage_request(self):
        pass

    def view_confirmed_apt(self):
        pass

    def input_prescription(self):
        pass
