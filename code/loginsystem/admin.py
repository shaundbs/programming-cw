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
