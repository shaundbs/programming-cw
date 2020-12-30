from state_manager import StateGenerator
import gp_database as db
import gp_utilities as util
import cli_ui as ui
from os import system
from tabulate import tabulate
from pandas import DataFrame
import sqlite3
from sqlite3 import Error
import bcrypt

states = {
    # admin menu    
    "Admin options": ["Manage patient", "Manage GP", "Register new GP", "Approve new patient", "Log out"],
    # Erfan's Options
    # Manage GP menu
    "Manage GP": ["Edit GP account Information", "Remove GP account", "Deactivate GP account", "Reactivate GP account", "Back"],
    # Edit GP menu
    "Edit GP account information": ["Change GP name", "Change GP registered email address", "Reset GP password", "Back"],
    "Change GP name": ["Back"],
    "Change GP registered email address": ["Back"],
    "reset GP password": ["Back"],
    # Other menus
    "Remove GP account": ["Back"],
    "Deactivate GP account": ["Back"],
    "Reactivate GP account": ["Back"],
    
}

class Admin():
    def __init__(self, user_id):
        # Create object from userId object from DB
        self.user_id = user_id

        # Get firstname and lastname of admin user 
        self.db = db.Database()
        details_query = f"SELECT FIRSTNAME, LASTNAME FROM USERS WHERE USERID = {user_id}"
        result = self.db.fetch_data(details_query)
        self.db.close_db()
        self.firstname, self.lastname = result[0]['firstName'].capitalize(), result[0]['lastName'].capitalize()

        # initialise state machine
        self.state_gen = StateGenerator(state_dict=states, state_object=self)
        self.state_gen.change_state("admin options") 

    def print_welcome(self):
        ui.info_section(ui.blue, 'Welcome to the GP Dashboard')
        print(f"Hi {self.firstname}")

    def handle_state_selection(self, selected):
        if selected == 'Back':
            self.state_gen.call_parent_state()
        else:
            self.state_gen.change_state(selected)

    def state_selection_with_argument(self, selected, arg):
        selected = selected.lower().replace(" ","_")
        arg = str(arg)  
        select = "self.to_" + selected + "(" + arg + ")"
        return select

    @staticmethod
    def clear():
        _ = system('clear')

    def admin_options(self):
        Admin.clear()
        self.print_welcome() 
        selected = util.user_select("Please choose one of the options above.", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def log_out(self):
        # TODO
        pass

    def manage_gp(self):
        Admin.clear()
        ui.info_section(ui.blue, 'Manage GP Menu')

        # show GPs in system
        self.db = db.Database()
        gp_acct_query = f"SELECT userID, firstName, lastName, email, is_active, is_registered FROM users WHERE accountType = 'gp'"
        gp_acct_result = self.db.fetch_data(gp_acct_query)
        self.db.close_db()
        gp_dataframe_header = ['ID', 'First Name', 'Last Name', 'email', 'Active?', 'Registered?']
        gp_dataframe = DataFrame(gp_acct_result)
        gp_dataframe.columns = gp_dataframe_header
        gp_table = tabulate(gp_dataframe, headers='keys', tablefmt='fancy_grid', showindex=False)
        print(gp_table)

        # allow admin user to choose desired gp account
        gp_id_list = gp_dataframe['ID'].tolist()
        gp_id_list.append("Back")
        gp_id = util.user_select("Please choose the ID of the GP you would like to manage: ", choices=gp_id_list)
        # if selected is gp_id
        if isinstance(gp_id, int):
            Admin.clear()
            ui.info_section(ui.blue, 'Manage GP Options')
            selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())
            if selected == "Edit GP account Information":
                self.to_edit_gp_account_information(gp_id)
            elif selected == "Remove GP account":
                self.to_remove_gp_account(gp_id)
            elif selected == "Deactivate GP account":
                self.to_deactivate_gp_account(gp_id)
            elif selected == "Reactivate GP account":
                self.to_reactivate_gp_account(gp_id)
            else:
                self.handle_state_selection("Manage GP")
        elif gp_id == "Back":
            self.handle_state_selection("Admin Options")

    def edit_gp_account_information(self, gp_id):
        Admin.clear()
        ui.info_section(ui.blue, 'Edit GP account?')
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())
        if selected == "Change GP name":
            self.to_change_gp_name(gp_id)
        elif selected == "Change GP registered email address":
            self.to_change_gp_registered_email_address(gp_id)
        elif selected == "Reset GP password":
            self.to_reset_gp_password(gp_id)
        else:
            self.handle_state_selection("Manage GP")

    def change_gp_name(self, gp_id):
        Admin.clear()
        ui.info_section(ui.blue, "Change GP's name?")
        change_name_confirm = ui.ask_yes_no("Are you sure you want to change the name of this GP's account?", default=False)
        if change_name_confirm == True:
            new_fName = ui.ask_string("Please enter the GP's new first name: ").capitalize()
            new_lName = ui.ask_string("Please enter the GP's new last name: ").capitalize()
            self.db = db.Database()
            self.db.exec_one("""UPDATE Users SET FirstName=?,LastName=? WHERE userID=?""", [new_fName, new_lName, gp_id])
            self.db.close_db()
            # ui.info_2(ui.standout, f"This account's name has been changed to: {new_fName} {new_lName}")
            self.state_gen.change_state("Manage GP") 
        else: 
            self.handle_state_selection("Manage GP")

    def change_gp_registered_email_address(self, gp_id):
        Admin.clear()
        ui.info_section(ui.blue, "Change GP's email ?")
        change_email_confirm = ui.ask_yes_no("Are you sure you want to change the email for this GP's account?", default=False)
        if change_email_confirm == True:
            new_email = ui.ask_string("Please enter the GP's new email: ")
            # TODO: input validation
            self.db = db.Database()
            self.db.exec_one("""UPDATE Users SET email=? WHERE userID=?""", [new_email, gp_id])
            self.db.close_db()
            # ui.info_2(ui.standout, f"This account's email has been changed to: {new_fName} {new_email}")
            self.state_gen.change_state("Manage GP") 
        else: 
            self.handle_state_selection("Manage GP")
    
    def reset_gp_password(self, gp_id):
        Admin.clear()
        ui.info_section(ui.blue, "Reset GP's password?")
        reset_password_confirm = ui.ask_yes_no("Are you sure you want to reset the password for this account?", default=False)
        if reset_password_confirm == True:
            new_password = ui.ask_password("Please enter a new password: ")
            # TODO: input validation - e.g. ask admin to input new password 

            # encode password
            new_password = new_password.encode('UTF-8')
            # hash password
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(new_password, salt)
            # update password in db
            self.db = db.Database()
            self.db.exec_one("""UPDATE Users SET password=?  WHERE userID=?""", [hashed_password, gp_id])
            self.db.close_db()
            # redirect to manage GP page
            self.handle_state_selection("Manage GP")
        else: 
            self.handle_state_selection("Manage GP")

    def remove_gp_account(self, gp_id):
        Admin.clear()
        ui.info_section(ui.blue, 'Remove GP account?')
        delete_gp_confirm = ui.ask_yes_no("Are you sure you want to permanently remove this GP account?", default=False)
        if delete_gp_confirm == True:
            self.db = db.Database()
            delete_gp_query = f"DELETE FROM Users WHERE userID= {gp_id}"
            self.db.exec(delete_gp_query)
            self.db.close_db()
            ui.info_2(ui.standout, f"This account has been deleted.")
            self.state_gen.change_state("Manage GP") 
        else: 
            self.handle_state_selection("Back")

    def deactivate_gp_account(self, gp_id):
        Admin.clear()
        ui.info_section(ui.blue, 'Deactivate GP account?')
        deactivate_gp_confirm = ui.ask_yes_no("Are you sure you want to deactivate this GP account?", default=False)
        if deactivate_gp_confirm == True:
            self.db = db.Database()
            deactivate_gp_query = f"UPDATE Users SET is_active=0 WHERE userID={gp_id}"
            self.db.exec(deactivate_gp_query)
            self.db.close_db()
            ui.info_2(ui.standout, f"This account has been deactivated.")
            self.state_gen.change_state("Manage GP") 
            
        else: 
            self.handle_state_selection("Back")

    def reactivate_gp_account(self, gp_id):
        Admin.clear()
        ui.info_section(ui.blue, 'Reactivate GP account?')
        reactivate_gp_confirm = ui.ask_yes_no("Are you sure you want to reactivate this GP account?", default=False)
        if reactivate_gp_confirm == True:
            self.db = db.Database()
            reactivate_gp_query = f"UPDATE Users SET is_active=1 WHERE userID={gp_id}"
            self.db.exec(reactivate_gp_query)
            self.db.close_db()
            ui.info_2(ui.standout, f"This account has been reactivated.")
            self.state_gen.change_state("Manage GP") 
        else: 
            self.handle_state_selection("Back")


