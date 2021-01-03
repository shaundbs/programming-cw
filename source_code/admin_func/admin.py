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
from registerGP import registerGP, confirmation
from confirmPatient import confirmPatient, validate, clear
from time import sleep

states = {
    # admin menu    
    "Admin options": ["Manage patient", "Manage GP", "Register new GP", "Approve new patient", "Log out"],
    "Manage patient": ["searchDOB", "searchname", "Back"],

    "Return to menu": ["Manage patient", "Manage GP", "Register new GP", "Approve new patients", "Log out"],

    # Register GP
    "Register new GP": ["Confirm details", "Back"],
    "Confirm details": ["Register another GP", "Return to menu"],
    "Register another GP": ["Confirm details", "Return to menu"],

    # Confirm Patient
    "Approve new patients": ["Continue validation", "Back"],
    "Continue validation": ["Validate more entries", "Return to menu"],
    "Validate more entries": ["Continue validation", "Return to menu"],

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
        ui.info_section(ui.blue, 'Welcome to the Admin Dashboard')
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

        # show GPs in system2
        self.db = db.Database()
        gp_acct_query = f"SELECT userID, firstName, lastName, email, is_active FROM users WHERE accountType = 'gp'"
        gp_acct_result = self.db.fetch_data(gp_acct_query)
        self.db.close_db()
        gp_dataframe_header = ['ID', 'First Name', 'Last Name', 'email', 'Active?']
        gp_dataframe = DataFrame(gp_acct_result)
        gp_dataframe.columns = gp_dataframe_header
        gp_table = tabulate(gp_dataframe, headers='keys', tablefmt='pretty', showindex=False)
        print(gp_table + "\n")

        # allow admin user to choose desired gp account
        # extract GP IDs
        gp_id_list = gp_dataframe['ID'].tolist()
        gp_id_list.append("Back")
        # Extract GP names
        gp_fname_list = gp_dataframe['First Name'].tolist()
        gp_lname_list = gp_dataframe['Last Name'].tolist()
        gp_name_list = [' '.join(z) for z in zip(gp_fname_list, gp_lname_list)]
        gp_list = ["Dr. "+ gp_name for gp_name in gp_name_list]
        gp_list.append("Back")
        # Create dictionary with GP IDs as keys and names as values 
        gp_dict = {k:v for k,v in zip(gp_list,gp_id_list)}
        # show admin user GP accounts they can manipulate 
        gp_person = util.user_select("Please choose the GP you would like to manage: ", choices=gp_list)
        # get id for chosen GP 
        gp_id = gp_dict[gp_person]

        # check if gp_id is received or whether admin user should be redirected to admin main menu
        if isinstance(gp_id, int):
            Admin.clear()
            ui.info_section(ui.blue, 'Manage GP Options')
            # show selected gp
            chosen_gp_df = gp_dataframe.loc[gp_dataframe['ID'] == gp_id]
            chosen_gp_table = tabulate(chosen_gp_df, headers='keys', tablefmt='grid', showindex=False)
            print(chosen_gp_table + "\n")
            # admin user selects what they want to do with desired gp account
            selected = util.user_select("Please choose what you would like to do with the GP account show above: ", self.state_gen.get_state_options())
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

    def register_new_gp(self):
        registerGP()
        selected = util.user_select("Please choose one of the options below.", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def confirm_details(self):
        confirmation()
        selected = util.user_select("Please choose one of the options below.", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def register_another_gp(self):
        self.register_new_gp()

    def approve_new_patients(self):
        try:
            confirmPatient()
            selected = util.user_select("Please choose one of the options below.", self.state_gen.get_state_options())
            self.handle_state_selection(selected)
        except:
            print("\nNo patients currently require validation!\nRedirecting...")
            sleep(3)
            self.to_admin_options()

    def continue_validation(self):
        validate()
        selected = util.user_select("Please choose one of the options below.", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def validate_more_entries(self):
        self.approve_new_patients()


    def return_to_menu(self):
        self.admin_options()