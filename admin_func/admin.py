import os
from os import system
from time import sleep
import re
from . import admin_database as db
from . import admin_utilities as util
import bcrypt
import cli_ui as ui
from .admin_database import Database
from .confirmPatient import confirm_patient, validate, approve_all, delete_all
from pandas import DataFrame
from .registerGP import registerGP, confirmation
from tabulate import tabulate
from termcolor import colored
import datetime
from datetime import date, datetime as Datetime
from state_manager import StateGenerator
from gp_func.gp import Gp
from sys import exit

states = {
    # admin menu
    "Admin options": ["Manage patient", "Manage GP", "Register new GP", "Approve new patients", "Assign new admin",
                      "View reports", "Log out"],
    "Return to menu": ["Manage patient", "Manage GP", "Register new GP", "Approve new patients", "Assign new admin",
                       "View reports", "Log out"],
    "Log out": [""],
    "Manage Patient": ["Search by Date of Birth", "Search by Last Name", "Back"],
    "Search by Date of Birth": ["Manage Patient Account"],
    "Search by Last Name": ["Manage Patient Account"],
    "Assign new admin": ["Back"],

    # data dashboard menu
    "View reports": ["GP report", "Patient report", "Specialist report", "Back"],
    "GP report": ["Back"],
    "Patient report": ["Back"],
    "Specialist report": ["Back"],

    # Manage GP menu
    "Manage GP": ["Edit GP account Information", "Remove GP account", "Deactivate GP account",
                  "Reactivate GP account", "Sign in as this GP", "Back"],

    # Edit GP menu
    "Edit GP account information": ["Change GP name", "Change GP registered email address", "Reset GP password",
                                    "Back"],
    "Change GP name": ["Back"],
    "Change GP registered email address": ["Back"],
    "reset GP password": ["Back"],

    # Other Manage GP menu options
    "Remove GP account": ["Back"],
    "Deactivate GP account": ["Back"],
    "Reactivate GP account": ["Back"],
    "Sign in as this GP": ["Back"],

    # Register GP
    "Register new GP": ["Confirm details", "Back"],
    "Confirm details": ["Register another GP", "Return to menu"],
    "Register another GP": ["Confirm details", "Return to menu"],
    # Confirm Patient
    "Approve new patients": ["Continue validation", "Approve all patients", "Delete all patients", "Back"],
    "Continue validation": ["Validate more entries", "Return to menu"],
    "Validate more entries": ["Continue validation", "Return to menu"],
    "Approve all patients": ["Return to menu"],
    "Delete all patients": ["Return to menu"],

    # Manage Patient menu
    "Manage Patient Account": ["Edit Patient Details", "Add Medical History", "Delete Medical History",
                               "Deactivate Patient Account", "Reactivate Patient Account","Download Patient Record",
                               "Back"],
    "Edit Patient Details": ["Change Patient name", "Change Date of Birth", "Change Patient email address", "Back"],
    "Add Medical History": ["Add to the Medical History", "Back"],
    "Delete Medical History": ["Delete Medical History", "Back"],
    "Deactivate Patient Account": ["Deactivate the Patients account", "Back"],
    "Reactivate Patient Account": ["Reactivate the Patients account", "Back"],
    "Download Patient Record": ["Download the Patient Record", "Back"],
}


class Admin:
    def __init__(self, user_id):
        # Create object from userId object from DB
        self.user_id = user_id
        # Get firstname and lastname of admin user
        self.db = db.Database()
        details_query = f"SELECT firstname, LASTNAME FROM USERS WHERE USERID = {user_id}"
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
        if selected.lower() == "back":
            self.state_gen.call_parent_state()
        else:
            self.state_gen.change_state(selected)

    @staticmethod
    def state_selection_with_argument(selected, arg):
        selected = selected.lower().replace(" ", "_")
        arg = str(arg)
        select = "self.to_" + selected + "(" + arg + ")"
        return select

    @staticmethod
    def clear():
        _ = os.system('cls' if os.name == 'nt' else 'clear')

    def admin_options(self):
        Admin.clear()
        self.print_welcome()

        # instructions
        ui.info(ui.faint, "\nInfo:"
                          "\n'Manage patient' to search for patient records by DOB or last name. "
                          "\n\tOnce a patient record is found, you can: edit patient details, "
                          "medical history and account status."
                          "\n'Manage GP' to sign as selected GP user, "
                          "edit specific GP account information and account status."
                          "\n'Register new GP' to appoint a new GP."
                          "\n'Approve new patients' to validate newly registered patients."
                          "\n'Assign new admin' to appoint a new user with admin privileges."
                          "\n'View reports' to track user metrics. \n")

        # State management
        selected = util.user_select("Please choose one of the options below.", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def log_out(self):
        # remove state tracking from the object.
        Admin.clear()
        del self.state_gen
        # Exit program with animation
        print(" ")
        util.loader("Logging out")
        print(" ")
        exit()


    def manage_gp(self):
        Admin.clear()
        ui.info_section(ui.blue, 'Manage GP Menu')

        # Show GP table
        # Query GP information
        self.db = db.Database()
        gp_acct_query = f"SELECT firstname, lastName, email, is_active, userID FROM users WHERE accountType = 'gp'"
        gp_acct_result = self.db.fetch_data(gp_acct_query)
        self.db.close_db()
        # Construct dataframe
        gp_dataframe_header = ['First Name', 'Last Name', 'email', 'Active?', 'ID']
        gp_dataframe = DataFrame(gp_acct_result)
        gp_dataframe.columns = gp_dataframe_header
        # tabulate gp dataframe
        gp_table = tabulate(gp_dataframe, headers='keys', tablefmt='grid', showindex=False)
        print(gp_table + "\n")

        # allow admin user to choose desired gp account
        # extract GP IDs
        gp_id_list = gp_dataframe['ID'].tolist()
        # add "back" State option
        gp_id_list.append("Back")
        # Extract GP names
        gp_fname_list = gp_dataframe['First Name'].tolist()
        gp_lname_list = gp_dataframe['Last Name'].tolist()
        # join first names and last names
        gp_name_list = [' '.join(z) for z in zip(gp_fname_list, gp_lname_list)]
        # join salutation and gp names
        gp_list = ["Dr. " + gp_name for gp_name in gp_name_list]
        # add "back" State option
        gp_list.append("Back")
        # Create dictionary with GP IDs as keys and names as values
        gp_dict = {k: v for k, v in zip(gp_list, gp_id_list)}
        # show admin user GP accounts they can manipulate
        gp_person = util.user_select("Please choose the GP you would like to manage: ", choices=gp_list)
        # get id for chosen GP
        gp_id = gp_dict[gp_person]

        # check if gp_id received, otherwise redirect admin user to admin menu
        if isinstance(gp_id, int):

            Admin.clear()
            ui.info_section(ui.blue, 'Manage GP Options')
            # show selected gp
            chosen_gp_df = gp_dataframe.loc[gp_dataframe['ID'] == gp_id]
            chosen_gp_table = tabulate(chosen_gp_df, headers='keys', tablefmt='grid', showindex=False)
            print(chosen_gp_table + "\n")
            # admin user selects what to do with chosen gp account -> state management
            selected = util.user_select("Please choose what you would like to do with the GP account show above: ",
                                        self.state_gen.get_state_options())
            if selected == "Edit GP account Information":
                self.to_edit_gp_account_information(gp_id, chosen_gp_table)
            elif selected == "Remove GP account":
                self.to_remove_gp_account(gp_id)
            elif selected == "Deactivate GP account":
                self.to_deactivate_gp_account(gp_id)
            elif selected == "Reactivate GP account":
                self.to_reactivate_gp_account(gp_id)
            elif selected == "Sign in as this GP":
                self.to_sign_in_as_this_gp(gp_id)
            else:
                self.handle_state_selection("Manage GP")
        elif gp_id == "Back":
            self.handle_state_selection("Admin Options")

    def edit_gp_account_information(self, gp_id, chosen_gp_table):
        Admin.clear()
        ui.info_section(ui.blue, 'Edit GP account')

        # recreate chose_gp table with only chosen GP
        self.db = db.Database()
        gp_acct_query = f"SELECT firstname, lastName, email, is_active, userID FROM users WHERE accountType = 'gp' " \
                        f"AND userID={gp_id}"
        gp_acct_result = self.db.fetch_data(gp_acct_query)
        self.db.close_db()
        gp_dataframe_header = ['First Name', 'Last Name', 'email', 'Active?', 'ID']
        gp_dataframe = DataFrame(gp_acct_result)
        gp_dataframe.columns = gp_dataframe_header
        chosen_gp_table = tabulate(gp_dataframe, headers='keys', tablefmt='grid', showindex=False)
        print(chosen_gp_table + "\n")

        # State management
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())
        if selected == "Change GP name":
            self.to_change_gp_name(gp_id, chosen_gp_table)
        elif selected == "Change GP registered email address":
            self.to_change_gp_registered_email_address(gp_id, chosen_gp_table)
        elif selected == "Reset GP password":
            self.to_reset_gp_password(gp_id, chosen_gp_table)
        else:
            self.handle_state_selection("Manage GP")

    def change_gp_name(self, gp_id, chosen_gp_table):
        Admin.clear()
        ui.info_section(ui.blue, "Change GP's name?")

        # name input validation
        while True:
            new_firstname = ui.ask_string("Please enter the GP's new first name: ").capitalize()
            if new_firstname.isalpha():
                break
            else:
                print("Please only include letters.")
        while True:
            new_lastname = ui.ask_string("Please enter the GP's new last name: ").capitalize()
            if new_lastname.isalpha():
                break
            else:
                print("Please only include letters.")

        # confirm user intent to change name
        name_changed_confirm = ui.ask_yes_no("Are you sure you want to change the name for this GP's account "
                                             "to the above?", default=False)
        # if intent not confirmed, redirect
        if not name_changed_confirm:
            self.to_edit_gp_account_information(gp_id, chosen_gp_table)
        # ...otherwise,change name
        else:
            self.db = db.Database()
            self.db.exec_one("""UPDATE Users SET firstname=?,LastName=? WHERE userID=?""",
                             [new_firstname, new_lastname, gp_id])
            self.db.close_db()
            ui.info_section(ui.blue, "")
            ui.info_2(ui.standout, f"Successfully updated GP's name to: {new_firstname} {new_lastname}. "
                                   f"Please wait whilst you are redirected.\n")
            util.loader('Loading')

            # State management
            self.to_edit_gp_account_information(gp_id, chosen_gp_table)

    def change_gp_registered_email_address(self, gp_id, chosen_gp_table):
        Admin.clear()
        ui.info_section(ui.blue, "Change GP's email ?")

        # email input validation
        change_email = True
        self.db = db.Database()
        email_list = self.db.email_list()
        while change_email:
            regex = '^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$'
            new_email = ui.ask_string("Please enter the GP's new email: ")
            # check email meets required format
            if not re.search(regex, new_email):
                print("Invalid Email. Please try again.")
            # check email does not already exist in system
            elif new_email in email_list:
                print('This email has already been registered. Please try again')
            else:
            # if requirements met, accept email
                new_email = new_email.lower()
                change_email = False
                break

        # confirm intent to change email
        email_changed_confirm = ui.ask_yes_no("Are you sure you want to change the email for this GP's account "
                                              "to the above?", default=False)

        # if intent is not confirmed, redirect user...
        if not email_changed_confirm:
            self.to_edit_gp_account_information(gp_id, chosen_gp_table)
        # ...otherwise, update database with new email
        else:
            self.db = db.Database()
            self.db.exec_one("""UPDATE Users SET email=? WHERE userID=?""", [new_email, gp_id])
            self.db.close_db()
            ui.info_section(ui.blue, "")
            ui.info_2(ui.standout, f"Successfully updated GP's email. Please wait whilst you are redirected.\n")
            util.loader('Loading')

            # state management
            self.to_edit_gp_account_information(gp_id, chosen_gp_table)

    def reset_gp_password(self, gp_id, chosen_gp_table):
        Admin.clear()
        ui.info_section(ui.blue, "Reset GP's password?")

        # confirm intent to reset password
        reset_password_confirm = ui.ask_yes_no("Are you sure you want to reset the password for this account?",
                                               default=False)

        # if intent to rest password confirmed,
        if reset_password_confirm:
            # retrieve GP's current password
            self.db = db.Database()
            old_password_query = f"SELECT password from Users WHERE userID = {gp_id}"
            old_password = self.db.fetch_data(old_password_query)
            old_password = old_password[0]['password']
            self.db.close_db()

            # If old password found,
            if old_password:
                # password validation
                is_long_enough = False
                while not is_long_enough:
                    # Prompt user for new password
                    # encode password
                    new_password = ui.ask_password('New Password: ')
                    if not isinstance(new_password, bytes):
                        new_password = new_password.encode('utf-8')
                    if not isinstance(old_password, bytes):
                        old_password = old_password.encode('utf-8')
                    # check length of password
                    if len(new_password) < 5:
                        print("The minimum length for a password is 5 characters. Please try again.")
                    # check password is not same as previous password
                    elif bcrypt.checkpw(new_password, old_password):
                        print('Your new password cannot be the same as your old password. Please try again.')
                    else:
                        # Prompt user for password confirm
                        new_password_confirm = ui.ask_password('Confirm your password:')
                        # encode password
                        if not isinstance(new_password_confirm, bytes):
                            new_password_confirm = new_password_confirm.encode('utf-8')
                        # if passwords pmatch
                        if new_password == new_password_confirm:
                            is_long_enough = True
                        else:
                            print("Your new password does not match the password confirmation. Please try again.\n")

                # hash password
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(new_password, salt)
                # update password in db
                self.db = db.Database()
                self.db.exec_one("""UPDATE Users SET password=?  WHERE userID=?""", [hashed_password, gp_id])
                self.db.close_db()
                # success notification
                ui.info_section(ui.blue, "")
                ui.info_2(ui.standout, f"Successfully reset GP's password. Please wait whilst you are redirected.\n")
                util.loader('Loading')
                # State management
                self.to_edit_gp_account_information(gp_id, chosen_gp_table)

        # if user has change of heart before changing password, redirect
        else:
            self.to_edit_gp_account_information(gp_id, chosen_gp_table)

    def remove_gp_account(self, gp_id):
        Admin.clear()
        ui.info_section(ui.blue, 'Remove GP account?')

        # confirm intent
        delete_gp_confirm = ui.ask_yes_no("Are you sure you want to permanently remove this GP account?", default=False)

        # if intent confirmed
        if delete_gp_confirm:
            # update database
            self.db = db.Database()
            delete_gp_query = f"DELETE FROM Users WHERE userID= {gp_id}"
            self.db.exec(delete_gp_query)
            self.db.close_db()
            # inform user
            ui.info_2(ui.standout, f"This account has been deleted.")
            # State management
            self.state_gen.change_state("Manage GP")

        # If user changes mind
        else:
            self.handle_state_selection("Back")

    def deactivate_gp_account(self, gp_id):
        Admin.clear()
        ui.info_section(ui.blue, 'Deactivate GP account?')

        # confirm deactivation intent
        deactivate_gp_confirm = ui.ask_yes_no("Are you sure you want to deactivate this GP account?", default=False)

        # If intent to deactivate is confirmed
        if deactivate_gp_confirm:

            # set GP user's active flag to False
            deactivate_gp_query = f"UPDATE Users " \
                                  f"SET is_active=0 " \
                                  f"WHERE userID={gp_id};"\
            # Set GP's unconfirmed appointments to rejected
            del_confirmed_appt_query = f"UPDATE Appointment " \
                                       f"SET is_confirmed=0 " \
                                       f"WHERE is_completed is not 1 " \
                                       f"AND gp_id={gp_id};"
            set_rejected_query = f"UPDATE Appointment " \
                                 f"SET is_rejected=1 " \
                                 f"WHERE is_completed is not 1 " \
                                 f"AND gp_id={gp_id};"

            # Execute queries
            self.db = db.Database()
            self.db.exec(deactivate_gp_query)
            self.db.exec(del_confirmed_appt_query)
            self.db.exec(set_rejected_query)
            self.db.close_db()

            # inform Admin user of changes
            ui.info_2(ui.standout, f"This account has been deactivated.")
            ui.info_2(ui.standout, f"All pending appointments have been set to rejected.")
            ui.info_2(ui.standout, f"Please wait to be redirected.\n")
            util.loader('Loading')

        # state management
            self.state_gen.change_state("Manage GP")

        # if reactivation intent is not confirmed
        else:
            self.handle_state_selection("Back")


    def reactivate_gp_account(self, gp_id):
        Admin.clear()
        ui.info_section(ui.blue, 'Reactivate GP account?')

        # confirm reactivation intent
        reactivate_gp_confirm = ui.ask_yes_no("Are you sure you want to reactivate this GP account?", default=False)

        # if intent to reactivate is confirmed
        if reactivate_gp_confirm:

            # set GP user's active flag to True
            reactivate_gp_query = f"UPDATE Users " \
                                  f"SET is_active=1 " \
                                  f"WHERE userID={gp_id};"

            # Set GP's unfinished appointments back to pending GP approval
            reset_confirmed_appts_query = f"  UPDATE Appointment " \
                                          f"SET is_confirmed=0 " \
                                          f"WHERE is_completed is not 1 " \
                                          f"AND gp_id={gp_id};"
            reset_rejected_appts_query = f"UPDATE Appointment " \
                                         f"SET is_rejected=0 " \
                                         f"WHERE is_completed is not 1 " \
                                         f"AND gp_id={gp_id};"

            # Execute queries
            self.db = db.Database()
            self.db.exec(reactivate_gp_query)
            self.db.exec(reset_confirmed_appts_query)
            self.db.exec(reset_rejected_appts_query)
            self.db.close_db()

            # inform Admin user of changes
            ui.info_2(ui.standout, f"This account has been reactivated.")
            ui.info_2(ui.standout, f"All incomplete appointments have been set back to pending.")
            ui.info_2(ui.standout, f"Please wait to be redirected.\n")
            util.loader('Loading')

            # state management
            self.state_gen.change_state("Manage GP")

        # if reactivation intent is not confirmed
        else:
            self.handle_state_selection("Back")


    def sign_in_as_this_gp(self, gp_id):

        # confirm sign in intent
        sign_in_as_gp_confirm = ui.ask_yes_no("Are you sure you want to sign in as this GP account?", default=False)

        # if intent confirmed
        if sign_in_as_gp_confirm:

            # view GP dashboard
            Gp(gp_id)

        # if sign in intent is not confirmed
        else:
            self.handle_state_selection("Back")

    def register_new_gp(self):
        registerGP()
        # State management
        selected = util.user_select("Please choose one of the options below.", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def confirm_details(self):
        confirmation()
        selected = util.user_select("Please choose one of the options below.", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def register_another_gp(self):
        self.register_new_gp()

    def approve_new_patients(self):
        # try:
        #     confirm_patient()
        #     selected = util.user_select("Please choose one of the options below.", self.state_gen.get_state_options())
        #     self.handle_state_selection(selected)
        # except:
        #     print("\nNo more patients currently require validation!\nRedirecting...")
        #     sleep(2)
        #     self.to_admin_options()
        confirm_patient()
        selected = util.user_select("Please choose one of the options below.", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    
    def approve_all_patients(self):
        approve_all()
        selected = util.user_select("Please choose one of the options below.", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def delete_all_patients(self):
        delete_all()
        selected = util.user_select("Please choose one of the options below.", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def continue_validation(self):
        validate()
        selected = util.user_select("Please choose one of the options below.", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def validate_more_entries(self):
        self.approve_new_patients()

    def return_to_menu(self):
        self.admin_options()

    # manage patient functionality
    # Find the Patient personal details and medical record and return them as two  dateframes
    @staticmethod
    def seepatientrecord(df):
        input_isvalid = True
        while input_isvalid:
            user_Input = input("Enter an ID Number from the table above to see a Patients Medical History: ")
            if not user_Input:
                print('Error: Invalid input')
            if user_Input.isdigit():
                id = int(user_Input)
                col_one_list = df['ID'].tolist()
                if id not in col_one_list:
                    print("Invalid ID input, Please select an ID from the table above")

                    # Return to original Menu
                else:
                    input_isvalid = False
            else:
                print("Invalid ID input, Please select an ID Number from the table above")

        index1 = ["UserID", "First Name", "Last Name", "date_of_birth", "email", "Role", "Registered", "Active",
                  "Signed UP"]
        index2 = ["MedicalHistoryID", "UserID", "illness", "time_afflicted", "description", "prescribed_medication"]
        db1 = Database()
        db1.exec_one(
            "SELECT userID, firstname, LastName, date_of_birth, email, accountType, is_registered, is_active, "
            "signUpDate FROM Users WHERE userID = ?",
            (id,))
        result = db1.c.fetchall()
        df1 = DataFrame(result)
        df1.columns = index1
        db2 = Database()
        db2.exec_one(
            "SELECT Medical_historyNo, userID, illness , time_afflicted, description, prescribed_medication FROM "
            "MedicalHistory WHERE userID = ?",
            (id,))
        result = db2.c.fetchall()
        row = len(result)
        print(row)

        if row == 0:

            db2.exec_one(
                "INSERT INTO MedicalHistory(userID, illness,time_afflicted,description,prescribed_medication) "
                "VALUES(?, ?,?, ?,?)",
                (id, "Empty", "Empty", "Empty", "Empty"))
            db2.exec_one(
                "SELECT Medical_historyNo, userID, illness , time_afflicted, description, prescribed_medication FROM "
                "MedicalHistory WHERE userID = ?",
                (id,))
            result = db2.c.fetchall()
            df2 = DataFrame(result)
            df2.columns = index2
            return id, df1, df2

        else:
            df2 = DataFrame(result)
            df2.columns = index2
            return id, df1, df2
    
    # Display and prrint the  Patient personal details and medical record.
    def display_patient_record(self):
        Admin.clear()
        db1 = Database()
        db1.exec_one(
            "SELECT userID, firstname, LastName, date_of_birth, email, accountType, is_registered, is_active, "
            "signUpDate  FROM Users WHERE userID = ?",
            (self.ID,))
        result = db1.c.fetchall()
        index1 = ["UserID", "First Name", "Last Name", "date_of_birth", "email", "Role", "Registered", "Active",
                  "Signed UP"]
        df1 = DataFrame(result)
        df1.columns = index1

        db2 = Database()
        db2.exec_one(
            "SELECT Medical_historyNo, userID, illness , time_afflicted, description, prescribed_medication FROM "
            "MedicalHistory WHERE userID = ?",
            (self.ID,))
        result = db2.c.fetchall()
        index2 = ["MedicalHistoryID", "UserID", "illness", "time_afflicted", "description", "prescribed_medication"]
        df2 = DataFrame(result)
        df2.columns = index2

        print(colored('Patient Personal Record', 'green', attrs=['bold']))
        print(tabulate(df1, headers='keys', tablefmt='grid', showindex=False))
        print(colored('Patient Medical History', 'green', attrs=['bold']))
        print(tabulate(df2, headers='keys', tablefmt='grid', showindex=False))
    # Display and print only  Patient personal details

    def display_patient_persrecord(self):
        Admin.clear()
        db1 = Database()
        db1.exec_one(
            "SELECT userID, firstname, LastName, date_of_birth, email, accountType, is_registered, is_active, "
            "signUpDate  FROM Users WHERE userID = ?",
            (self.ID,))
        result = db1.c.fetchall()
        index1 = ["UserID", "First Name", "Last Name", "date_of_birth", "email", "Role", "Registered", "Active",
                  "Signed UP"]
        df1 = DataFrame(result)
        df1.columns = index1

        print(colored('Patient Personal Record', 'green', attrs=['bold']))
        print(tabulate(df1, headers='keys', tablefmt='grid', showindex=False))

     # Search the patient details by Date of birth or last name
    def manage_patient(self):

        os.system('clear')

        ui.info_section(ui.blue, 'Manage Patient Options')
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())

        if selected is None:
            self.handle_state_selection("Manage Patient")

        if selected == "Search by Date of Birth":
            dob = input("Enter the Date of Birth  (Format: YYYY-MM-DD EXAMPLE: 1996-10-16): ")
            db = Database()
            index = ["ID", "First Name", "Last Name", "date_of_birth", "email", "Role", "Registered", "Active",
                     "Signed UP"]
            db.exec_one(
                "SELECT userID, firstname, LastName, date_of_birth, email, accountType, is_registered, is_active, "
                "signUpDate  FROM Users WHERE date_of_birth = ? and accountType=? ",
                (dob, 'patient'))
            result = db.c.fetchall()
            row = len(result)
            if row == 0:
                print("No result found, Check if the Birth Date was entered in the correct format: DD-MM-YYYY \n")
                util.loader('Loading')
                Admin.clear()
                self.to_manage_patient()

            else:
                df = DataFrame(result)
                df.columns = index
                print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
                seepatientrecord = self.seepatientrecord(df)
                self.ID = seepatientrecord[0]
                self.DF1 = seepatientrecord[1]
                self.DF2 = seepatientrecord[2]
                self.to_manage_patient_account()
        elif selected == "Search by Last Name":
            name = input("Enter the Last Name of the Patient: ")
            name = name.lower()
            db = Database()
            index = ["ID", "First Name", "Last Name", "date_of_birth", "email", "Role", "Registered", "Active",
                     "Signed UP"]
            db.exec_one(
                "SELECT userID, firstname, LastName, date_of_birth, email, accountType, is_registered, is_active, "
                "signUpDate  FROM Users WHERE lower(LastName) = ? and accountType=? ",
                (name, 'patient'))
            result = db.c.fetchall()
            row = len(result)
            if row == 0:
                print("No result found, Check if the Name was typed in correctly.\n")
                util.loader('Loading')
                Admin.clear()
                self.to_manage_patient()
            else:
                df = DataFrame(result)
                df.columns = index
                print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
                seepatientrecord = Admin.seepatientrecord(df)
                self.ID = seepatientrecord[0]
                self.DF1 = seepatientrecord[1]
                self.DF2 = seepatientrecord[2]
                self.to_manage_patient_account()
        elif selected == "Back":
            self.handle_state_selection("Admin Options")
    
    # State for all the patient managment option as Admin when a patient is selected
    def manage_patient_account(self):
        self.display_patient_record()
        ui.info_section(ui.blue, 'Manage Patient Account Options')
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())
        if selected == "Edit Patient Details":
            self.to_edit_patient_details()
        elif selected == "Add Medical History":
            self.to_add_medical_history()
        elif selected == "Delete Medical History":
            self.to_delete_medical_history()
        elif selected == "Deactivate Patient Account":
            self.to_deactivate_patient_account()
        elif selected == "Reactivate Patient Account":
            self.to_reactivate_patient_account()
        elif selected == "Download Patient Record":
            self.to_download_patient_record()
        elif selected == "Back":
            self.handle_state_selection("Admin Options")
            
    # Edit all the patient's personal details (Name, Date of birth, email)
    def edit_patient_details(self):
        self.display_patient_persrecord()
        ui.info_section(ui.blue, 'Edit Patient Personal Account Options')
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())

        if selected == "Change Patient name":
            while True:
                FirstName = ui.ask_string("Please enter the Patient's new first name: ").capitalize()
                if FirstName.isalpha():
                    break
                else:
                    print("Please only include letters.")
            while True:
                LastName = ui.ask_string("Please enter the Patient's new last name: ").capitalize()
                if LastName.isalpha():
                    break
                else:
                    print("Please only include letters.")
            db = Database()
            db.exec_one("""UPDATE Users SET firstname=?,LastName=?  WHERE userID=?""", (FirstName, LastName, self.ID,))
            ui.info_2(ui.standout, f"Successfully Updated Patient Name. "
                                   f"Please wait whilst you are redirected.\n")
            util.loader('Loading')
            Admin.clear()
            self.edit_patient_details()
        elif selected == "Change Date of Birth":
            Check_Date_of_birth = True
            while Check_Date_of_birth:
                DoB = util.get_user_date()
                user_input = Datetime.strptime(DoB, "%Y-%m-%d")
                today = Datetime.now()
                if today.date() > user_input.date():
                    Check_Date_of_birth = False
                else:
                    print("Date of Birth cannot be set in the future!")
            db = Database()
            db.exec_one("""UPDATE Users SET date_of_birth=?  WHERE userID=?""", (DoB, self.ID,))
            ui.info_2(ui.standout, f"Successfully Updated Date of Birth. "
                                   f"Please wait whilst you are redirected.\n")
            util.loader('Loading')
            Admin.clear()
            self.edit_patient_details()

        elif selected == "Change Patient email address":
            email_repetition = True
            while email_repetition:
                regex = '^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$'
                email = input('Email:')
                if not re.search(regex, email):
                    print("Invalid Email. Please try again.")
                else:
                    email_repetition = False

            db = Database()
            db.exec_one("""UPDATE Users SET email=?  WHERE userID=?""", (email, self.ID,))
            ui.info_2(ui.standout, f"Successfully Updated the email. "
                                   f"Please wait whilst you are redirected.\n")
            util.loader('Loading')
            Admin.clear()
            self.edit_patient_details()
        elif selected == "Back":
            self.handle_state_selection("Back")

    # Add to the patient's Medical history
    def add_medical_history(self):
        self.display_patient_record()
        ui.info_section(ui.blue, 'Add Medical History')
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())

        if selected == "Add to the Medical History":

            db1 = Database()
            db1.exec_one(
                "SELECT Medical_historyNo, userID, illness , time_afflicted, description, prescribed_medication "
                "FROM MedicalHistory WHERE userID = ?",
                (self.ID,))
            result = db1.c.fetchall()
            row = len(result)
            ref = result[0]['illness']

            while True:
                illness= input("Illness (Character limit:30): ")
                if len(illness) > 30:
                    print("Error! Only 30 characters allowed!")
                else:
                    break
            while True:
                time_afflicted= input("time afflicted (Character limit:30): ")
                if len(time_afflicted) > 30:
                    print("Error! Only 20 characters allowed!")
                else:
                    break
            description = util.get_multi_line_input("Description (Start a new line after roughly 40 characters):")
            prescribed_medication = util.get_multi_line_input("Prescribed Medication (Start a new line after roughly 40 characters):")
            db1 = Database()

            if row == 1 and ref == "Empty":
                mednr = result[0]['Medical_historyNo']

                db1.exec_one("""UPDATE MedicalHistory SET illness=?,time_afflicted=?,description=?, 
                                prescribed_medication=? WHERE Medical_historyNo=?""",
                             (illness, time_afflicted, description, prescribed_medication, mednr,))
                ui.info_2(ui.standout, f"Medical History was added to the Patients record."
                                       f"Please wait whilst you are redirected.\n")
                util.loader('Loading')
                self.add_medical_history()
            else:

                db1.exec_one(
                    "INSERT INTO MedicalHistory(userID, illness,time_afflicted,description,prescribed_medication) "
                    "VALUES(?, ?,?, ?,?)",
                    (self.ID, illness, time_afflicted, description, prescribed_medication))
                ui.info_2(ui.standout, f"Medical History was added to the Patients record."
                                       f"Please wait whilst you are redirected.\n")
                util.loader('Loading')
                self.add_medical_history()
        elif selected == "Back":
            self.handle_state_selection("Back")

     # Add to the patient's Medical history
    def delete_medical_history(self):
        self.display_patient_record()
        ui.info_section(ui.blue, 'Delete Medical History')
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())
        if selected == "Delete Medical History":

            db1 = Database()
            db1.exec_one(
                "SELECT Medical_historyNo, userID, illness , time_afflicted, description, prescribed_medication "
                "FROM MedicalHistory WHERE userID = ?",
                (self.ID,))
            result = db1.c.fetchall()
            row = len(result)
            df = DataFrame(result)
            if row == 1:

                input_isvalid = True
                while input_isvalid:
                    user_Input = input("Enter an ID Number from the table above to see a Patients Medical History:")
                    if not user_Input:
                        print('Error: Invalid input')
                    if user_Input.isdigit():
                        nr = int(user_Input)
                        col_one_list = df['Medical_historyNo'].tolist()
                        if nr not in col_one_list:
                            print("Invalid Input, Please select an a MedicalHistoryNr from the table above:")
                        else:
                            input_isvalid = False
                    else:
                        print("Invalid Input, Please select an a MedicalHistoryNr from the table above:")

                db1 = Database()
                db1.exec_one("""UPDATE MedicalHistory SET illness=?,time_afflicted=?,description=?, 
                                prescribed_medication=? WHERE Medical_historyNo=?""",
                             ("Empty", "Empty", "Empty", "Empty", nr,))
                ui.info_2(ui.standout, f"Selected  Medical History was deleted from the Patients record."
                                       f"Please wait whilst you are redirected.\n")
                util.loader('Loading')

                self.delete_medical_history()
            else:

                input_isvalid = True
                while input_isvalid:
                    user_Input = input("Enter an ID Number from the table above to see a Patients Medical History:")
                    if not user_Input:
                        print('Error: Invalid input')
                    if user_Input.isdigit():
                        nr = int(user_Input)
                        col_one_list = df['Medical_historyNo'].tolist()
                        if nr not in col_one_list:
                            print("Invalid Input, Please select an a MedicalHistoryNr from the table above:")
                        else:
                            input_isvalid = False
                db1 = Database()
                db1.exec_one("DELETE FROM MedicalHistory WHERE Medical_historyNo=?", (nr,))
                ui.info_2(ui.standout, f"Selected  Medical History was deleted from the Patients record."
                                       f"Please wait whilst you are redirected.\n")
                util.loader('Loading')
                self.delete_medical_history()
        elif selected == "Back":
            self.handle_state_selection("Back")
            
     # Deactivate a patient's Account.
    def deactivate_patient_account(self):
        self.display_patient_persrecord()
        ui.info_section(ui.blue, 'Deactivate Personal Account Options')
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())

        if selected == "Deactivate the Patients account":
            db = Database()
            db.exec_one("""UPDATE Users SET is_active=0  WHERE userID=?""", (self.ID,))
            ui.info_2(ui.standout, f"Patients account has been deactivated. "
                                   f"Please wait whilst you are redirected.\n")
            util.loader('Loading')
            self.deactivate_patient_account()
        elif selected == "Back":
            self.handle_state_selection("Manage Patient Account")
            
     # Reactivate a patient's Account.
    def reactivate_patient_account(self):
        self.display_patient_persrecord()

        ui.info_section(ui.blue, 'Reactivate Personal Account Options')
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())

        if selected == "Reactivate the Patients account":
            db = Database()
            db.exec_one("""UPDATE Users SET is_active=1  WHERE userID=?""", (self.ID,))
            ui.info_2(ui.standout, f"Patients account has been reactivated. "
                                   f"Please wait whilst you are redirected.\n")
            util.loader('Loading')
            self.reactivate_patient_account()
        elif selected == "Back":
            self.handle_state_selection("Manage Patient Account")

    def view_reports(self):
        Admin.clear()
        ui.info_section(ui.blue, "Performance metrics")

        # State management
        selected = util.user_select("Please choose the trackable metric you would like to view below.",
                                    self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def gp_report(self):
        Admin.clear()
        ui.info_section(ui.blue, "GP metrics report")

        all_gp_query = f'SELECT u.firstName ||" "|| u.lastName AS gp_name, ' \
                       f'CASE when is_active is null then "-" when is_active = 1 then "Yes" ' \
                       f'when is_active = 0 then "No" END AS "Account Active?", ' \
                       f'signUpDate, ' \
                       f'userId as GP_ID ' \
                       f'FROM Users u ' \
                       f'WHERE accountType="gp"'

        no_gp_holiday_query = f"select count(distinct gp_id) as no_gps_currently_off from gp_time_off where 'now' " \
                              f"between startTime and endTime"

        no_holidays_taken_query = f"SELECT firstName || ' ' || lastName as gp_name, " \
                                  f"sum(strftime('%d', endtime) - strftime('%d', starttime)) as no_days " \
                                  f"from gp_time_off g left join Users u on u.userId = g.gp_id " \
                                  f"where startTime between date('now', '-1 year') and date('now') " \
                                  f"group by gp_id, gp_name"

        gp_performance_query = f"SELECT u.firstName ||' '|| u.lastName as gp_name, " \
                               f"sum(is_confirmed) as no_confirmed_appts, " \
                               f"sum(is_rejected)  as no_rejected_appts, " \
                               f"count(appointment_id) as total_appts_requested, " \
                               f"printf('%.d',round((sum(is_confirmed)*100)/count(appointment_id))) " \
                               f"as confirmation_rate, " \
                               f"printf('%.d',round((sum(is_rejected)*100)/count(appointment_id))) " \
                               f"as rejection_rate " \
                               f"FROM Appointment a " \
                               f"LEFT JOIN Users u ON u.userId = a.gp_id " \
                               f"GROUP BY gp_name"

        # retrieve SQL results
        self.db = db.Database()
        all_gp_result = self.db.fetch_data(all_gp_query)
        no_gp_holiday_result = self.db.fetch_data(no_gp_holiday_query)
        no_holidays_taken_result = self.db.fetch_data(no_holidays_taken_query)
        gp_performance_result = self.db.fetch_data(gp_performance_query)
        self.db.close_db()

        # dataframe for all GPs and activity status
        all_gp_header_1 = colored('GP: ', 'cyan', attrs=['bold'])
        all_gp_header_2 = colored('Account active? ', 'cyan', attrs=['bold'])
        all_gp_header_3 = colored('Sign up date: ', 'cyan', attrs=['bold'])
        all_gp_header_4 = colored('ID: ', 'cyan', attrs=['bold'])
        all_gp_header = []
        all_gp_header.extend([all_gp_header_1, all_gp_header_2, all_gp_header_3, all_gp_header_4])
        all_gp_table = util.df_creator(all_gp_header, 'GPs', all_gp_result)
        print(all_gp_table + "\n")

        # dataframe showing number of GPs on holiday
        no_gp_holidays_header = [colored('Number of GPs on holiday: ', 'cyan', attrs=['bold'])]
        gp_holidays_table = util.df_creator(no_gp_holidays_header, 'Current holidays', no_gp_holiday_result)
        print(gp_holidays_table + "\n")

        # dataframe showing number of holiday days taken
        no_holidays_header_1 = colored('GP: ', 'cyan', attrs=['bold'])
        no_holidays_header_2 = colored('Number of holiday days taken this year: ', 'cyan', attrs=['bold'])
        no_holidays_header = []
        no_holidays_header.extend([no_holidays_header_1, no_holidays_header_2])
        no_holidays_table = util.df_creator(no_holidays_header, 'Holiday days taken', no_holidays_taken_result)
        print(no_holidays_table + "\n")

        # dataframe showing gp appointment performance
        gp_perf_header_1 = colored('GP: ', 'cyan', attrs=['bold'])
        gp_perf_header_2 = colored('confirmed appointments: ', 'cyan', attrs=['bold'])
        gp_perf_header_3 = colored('Rejected appointments: ', 'cyan', attrs=['bold'])
        gp_perf_header_4 = colored('Requested appointments: ', 'cyan', attrs=['bold'])
        gp_perf_header_5 = colored('confirmation rate (%): ', 'cyan', attrs=['bold'])
        gp_perf_header_6 = colored('rejection rate (%): ', 'cyan', attrs=['bold'])
        gp_perf_header = []
        gp_perf_header.extend([gp_perf_header_1, gp_perf_header_2, gp_perf_header_3, gp_perf_header_4,
                               gp_perf_header_5, gp_perf_header_6])
        gp_perf_table = util.df_creator(gp_perf_header, 'Appointment performance', gp_performance_result)
        print(gp_perf_table + "\n")

        # state management
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())
        self.handle_state_selection(selected)


    def patient_report(self):
        Admin.clear()
        ui.info_section(ui.blue, "Patient metrics report")

        patients_query = f'SELECT u.firstName ||" "|| u.lastName, CASE when is_registered is null then "-" ' \
                         f'when is_registered = 1 then "Yes" when is_registered = 0 then "No" END AS "Registered?",  ' \
                         f'CASE when is_active is null then "-" when is_active = 1 then "Yes" ' \
                         f'when is_active = 0 then "No" END AS "Account Active?", ' \
                         f'CASE when date_of_birth is null then "-" ' \
                         f'when date_of_birth is not null then date_of_birth END, ' \
                         f'signUpDate ' \
                         f'FROM Users u WHERE accountType="patient"'

        # pending_appt_query = f"SELECT appointment_id, " \
        #                       f"u.firstName ||' '|| u.lastName AS patient_name, " \
        #                       f"a.patient_id, " \
        #                       f"a.gp_id " \
        #                       f"FROM Appointment a " \
        #                       f"LEFT JOIN Users u ON a.patient_id=u.userId " \
        #                       f"LEFT JOIN Users on a.gp_id=u.userId " \
        #                       f"WHERE is_confirmed = 0 AND is_rejected = 0"

        pending_appt_query = f"SELECT appointment_id, " \
                             f"u.firstName ||' '|| u.lastName AS patient_name, " \
                             f"a.patient_id, " \
                             f"u2.firstName ||' '|| u2.lastName AS gp_name, " \
                             f"a.gp_id " \
                             f"FROM Appointment a " \
                             f"LEFT JOIN Users u ON a.patient_id=u.userId " \
                             f"left join Users u2 on a.gp_id=u2.userId " \
                             f"WHERE is_confirmed = 0 AND is_rejected = 0;"


        appt_referrals_query = f"SELECT appointment_id, " \
                               f"u.firstName ||' '|| u.lastName AS patient_name, " \
                               f"s.firstName ||' '|| s.lastName AS specialist_name, " \
                               f"s.hospital, d.name as 'Department' " \
                               f"FROM Appointment a LEFT JOIN users u ON a.patient_id=u.userId " \
                               f"LEFT JOIN Specialists s on a.referred_specialist_id=s.specialist_id " \
                               f"LEFT JOIN Department d on d.department_id=s.department_id " \
                               f"WHERE referred_specialist_id is not NULL"

        # sql fetch results
        self.db = db.Database()
        patients_result = self.db.fetch_data(patients_query)
        pending_appt_result = self.db.fetch_data(pending_appt_query)
        appt_referrals_result = self.db.fetch_data(appt_referrals_query)
        self.db.close_db()

        # dataframe for all patients
        patients_header_1 = colored('Patient: ', 'cyan', attrs=['bold'])
        patients_header_2 = colored('Registration approved?: ', 'cyan', attrs=['bold'])
        patients_header_3 = colored('Active account?: ', 'cyan', attrs=['bold'])
        patients_header_4 = colored('Date of birth (DOB): ', 'cyan', attrs=['bold'])
        patients_header_5 = colored('Sign up date: ', 'cyan', attrs=['bold'])
        patients_header = []
        patients_header.extend([patients_header_1, patients_header_2, patients_header_3,
                                patients_header_4, patients_header_5])
        patients_table = util.df_creator(patients_header, 'Patients', patients_result)
        print(patients_table + "\n")

        # # dataframe for pending appointments
        # pending_appt_header_1 = colored('Appointment number: ', 'cyan', attrs=['bold'])
        # pending_appt_header_2 = colored('Patient: ', 'cyan', attrs=['bold'])
        # pending_appt_header_3 = colored('Patient ID: ', 'cyan', attrs=['bold'])
        # pending_appt_header_4 = colored('GP ID: ', 'cyan', attrs=['bold'])
        # pending_appt_header = []
        # pending_appt_header.extend([pending_appt_header_1, pending_appt_header_2,
        #                             pending_appt_header_3, pending_appt_header_4])
        # pending_appt_table = util.df_creator(pending_appt_header, 'Pending Appointments', pending_appt_result)
        # print(pending_appt_table + "\n")

        # dataframe for pending appointments
        pending_appt_header_1 = colored('Appointment number: ', 'cyan', attrs=['bold'])
        pending_appt_header_2 = colored('Patient: ', 'cyan', attrs=['bold'])
        pending_appt_header_3 = colored('Patient ID: ', 'cyan', attrs=['bold'])
        pending_appt_header_4 = colored('GP: ', 'cyan', attrs=['bold'])
        pending_appt_header_5 = colored('GP ID: ', 'cyan', attrs=['bold'])
        pending_appt_header = []
        pending_appt_header.extend([pending_appt_header_1, pending_appt_header_2,
                                    pending_appt_header_3, pending_appt_header_4, pending_appt_header_5])
        pending_appt_table = util.df_creator(pending_appt_header, 'Pending Appointments', pending_appt_result)
        print(pending_appt_table + "\n")

        # dataframe for appointments which resulted in referral
        appt_referrals_header_1 = colored('Appointment ID:  ', 'cyan', attrs=['bold'])
        appt_referrals_header_2 = colored('Patient: ', 'cyan', attrs=['bold'])
        appt_referrals_header_3 = colored('Specialist: ', 'cyan', attrs=['bold'])
        appt_referrals_header_4 = colored('Specialist\'s hospital: ', 'cyan', attrs=['bold'])
        appt_referrals_header_5 = colored('Specialist\'s department: ', 'cyan', attrs=['bold'])
        appt_referrals_header = []
        appt_referrals_header.extend([appt_referrals_header_1, appt_referrals_header_2, appt_referrals_header_3,
                                      appt_referrals_header_4, appt_referrals_header_5])
        appt_referrals_table = util.df_creator(appt_referrals_header, 'Patient referrals', appt_referrals_result)
        print(appt_referrals_table + "\n")

        # state management
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def specialist_report(self):
        Admin.clear()
        ui.info_section(ui.blue, "Specialist metrics Report")

        specialists_dept_query = f"select name as department_name, count(specialist_id) as no_available_specialists from Department d left join Specialists s using(department_id) group by name"

        specialists_hosp_query = f"select hospital as Hospital, count(specialist_id) as no_available_specialists FROM Specialists WHERE hospital is not null GROUP BY hospital"

        specialists_query = f"SELECT specialist_id AS specialist_ID, firstName || ' ' || lastName as Specialist_name, Hospital , name FROM Specialists s LEFT JOIN Department d on d.department_id=s.department_id"

        # sql fetch results
        self.db = db.Database()
        specialists_dept_result = self.db.fetch_data(specialists_dept_query)
        specialists_hosp_result = self.db.fetch_data(specialists_hosp_query)
        specialists_result = self.db.fetch_data(specialists_query)
        self.db.close_db()

        # dataframe for specialists per department
        specialists_dept_header_1 = colored('Department: ', 'cyan', attrs=['bold'])
        specialists_dept_header_2 = colored('Number of available specialists: ', 'cyan', attrs=['bold'])
        specialists_dept_header = []
        specialists_dept_header.extend([specialists_dept_header_1, specialists_dept_header_2])
        specialists_dept_table = util.df_creator(specialists_dept_header, 'Specialists Departments', specialists_dept_result)
        print(specialists_dept_table + "\n")

        # dataframe for specialists per hospital
        specialists_hosp_header_1 = colored('Hospital: ', 'cyan', attrs=['bold'])
        specialists_hosp_header_2 = colored('Number of available specialists: ', 'cyan', attrs=['bold'])
        specialists_hosp_header = []
        specialists_hosp_header.extend([specialists_hosp_header_1, specialists_hosp_header_2])
        specialists_hosp_table = util.df_creator(specialists_hosp_header, 'Specialists Hospitals', specialists_hosp_result)
        print(specialists_hosp_table + "\n")

        # dataframe for specialists
        specialists_header_1 = colored('Specialist ID: ', 'cyan', attrs=['bold'])
        specialists_header_2 = colored('Specialist: ', 'cyan', attrs=['bold'])
        specialists_header_3 = colored('Hospital: ', 'cyan', attrs=['bold'])
        specialists_header_4 = colored('Department: ', 'cyan', attrs=['bold'])
        specialists_header = []
        specialists_header.extend(
            [specialists_header_1, specialists_header_2, specialists_header_3, specialists_header_4])
        specialists_table = util.df_creator(specialists_header, 'Specialists', specialists_result)
        print(specialists_table + "\n")

        # state management
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())
        self.handle_state_selection(selected)


    
    def download_patient_record(self):
        self.display_patient_persrecord()



        ui.info_section(ui.blue, 'Download Patient Record')
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())

        if selected == "Download the Patient Record":
            db1 = Database()
            db1.exec_one(
                "SELECT userID, firstname, LastName, date_of_birth, email, accountType, is_registered, is_active, "
                "signUpDate  FROM Users WHERE userID = ?",
                (self.ID,))
            result = db1.c.fetchall()
            index1 = ["UserID", "First Name", "Last Name", "date_of_birth", "email", "Role", "Registered", "Active",
                      "Signed UP"]
            df1 = DataFrame(result)
            df1.columns = index1

            no_space_name = result[0]['firstName'] + "_" + result[0]['lastName']

            db2 = Database()
            db2.exec_one(
                "SELECT Medical_historyNo, userID, illness , time_afflicted, description, prescribed_medication FROM "
                "MedicalHistory WHERE userID = ?",
                (self.ID,))
            result= db2.c.fetchall()
            index2 = ["MedicalHistoryID", "UserID", "illness", "time_afflicted", "description", "prescribed_medication"]
            df2 = DataFrame(result)
            df2.columns = index2
            curr_date = datetime.datetime.now()
            format_date = curr_date.strftime("%m_%d_%Y_%H_%M_%S_")
            file_name = format_date+no_space_name+"_Patient_record.csv"
            curr_dir = os.path.abspath(os.getcwd())
            dir_name = "downloaded_data"
            # check file path and directory exists, if not create it
            save_path = os.path.join(curr_dir, dir_name)
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            csv_file = os.path.join(save_path, file_name)
            result = df1.append(df2, sort=False)
            result.to_csv(csv_file, index=False)

            print(save_path)
            ui.info_2(ui.standout, f"Patients Record was downloaded and saved in the path above."
                                   f"Please wait whilst you are redirected.")
            sleep(3)
            self.download_patient_record()
        elif selected == "Back":
            self.handle_state_selection("Manage Patient Account")
           
       
     # Assign an new Admin Account.
    def download_patient_record(self):
        self.display_patient_persrecord()



        ui.info_section(ui.blue, 'Download Patient Record')
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())

        if selected == "Download the Patient Record":
            db1 = Database()
            db1.exec_one(
                "SELECT userID, firstname, LastName, date_of_birth, email, accountType, is_registered, is_active, "
                "signUpDate  FROM Users WHERE userID = ?",
                (self.ID,))
            result = db1.c.fetchall()
            index1 = ["UserID", "First Name", "Last Name", "date_of_birth", "email", "Role", "Registered", "Active",
                      "Signed UP"]
            df1 = DataFrame(result)
            df1.columns = index1

            no_space_name = result[0]['firstName'] + "_" + result[0]['lastName']

            db2 = Database()
            db2.exec_one(
                "SELECT Medical_historyNo, userID, illness , time_afflicted, description, prescribed_medication FROM "
                "MedicalHistory WHERE userID = ?",
                (self.ID,))
            result= db2.c.fetchall()
            index2 = ["MedicalHistoryID", "UserID", "illness", "time_afflicted", "description", "prescribed_medication"]
            df2 = DataFrame(result)
            df2.columns = index2
            curr_date = datetime.datetime.now()
            format_date = curr_date.strftime("%m_%d_%Y_%H_%M_%S_")
            file_name = format_date+no_space_name+"_Patient_record.csv"
            curr_dir = os.path.abspath(os.getcwd())
            dir_name1 = "downloaded_data"
            dir_name2 = "Medical_history"
            parent_dir = os.path.abspath(os.getcwd())
            path = os.path.join(parent_dir, dir_name1)
            path_join = os.path.join(path, dir_name2)

            # check file path and directory exists, if not create it
            save_path = os.path.join(curr_dir, path_join)
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            csv_file = os.path.join(save_path, file_name)
            result = df1.append(df2, sort=False)
            result.to_csv(csv_file, index=False)

            print(save_path)
            ui.info_2(ui.standout, f"Patients Record was downloaded and saved in the path above."
                                   f"Please wait whilst you are redirected.")
            sleep(3)
            self.download_patient_record()
        elif selected == "Back":
            self.handle_state_selection("Manage Patient Account")


