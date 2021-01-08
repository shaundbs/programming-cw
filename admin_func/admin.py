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


states = {
    # admin menu
    "Admin options": ["Manage patient", "Manage GP", "Register new GP", "Approve new patients", "Assign new admin",
                      "Track Performance", "Log out"],
    "Return to menu": ["Manage patient", "Manage GP", "Register new GP", "Approve new patients", "Assign new admin",
                       "Track Performance", "Log out"],
    "Log out": [""],
    "Manage Patient": ["Search by Date of Birth", "Search by Last Name", "Back"],
    "Search by Date of Birth": ["Manage Patient Account"],
    "Search by Last Name": ["Manage Patient Account"],
    "Assign new admin": ["Back"],

    # data dashboard menu
    "Track Performance": ["GP Metrics", "Patient Metrics", "Prescription Metrics", "Back"],
    "GP Metrics": ["Back"],
    "patient Metrics": ["Back"],
    "Prescription Metrics": ["Back"],

    # Manage GP menu
    "Manage GP": ["Edit GP account Information", "Remove GP account", "Deactivate GP account", "Reactivate GP account",
                  "Back"],

    # Edit GP menu
    "Edit GP account information": ["Change GP name", "Change GP registered email address", "Reset GP password",
                                    "Back"],
    "Change GP name": ["Back"],
    "Change GP registered email address": ["Back"],
    "reset GP password": ["Back"],
    # Other menus
    "Remove GP account": ["Back"],
    "Deactivate GP account": ["Back"],
    "Reactivate GP account": ["Back"],

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
                               "Deactivate Patient Account", "Reactivate Patient Account", "Back"],
    "Edit Patient Details": ["Change Patient name", "Change Date of Birth", "Change Patient email address", "Back"],
    "Add Medical History": ["Add to the Medical History", "Back"],
    "Delete Medical History": ["Delete Medical History", "Back"],
    "Deactivate Patient Account": ["Deactivate the Patients account", "Back"],
    "Reactivate Patient Account": ["Reactivate the Patients account", "Back"],

}


class Admin:
    def __init__(self, user_id):
        # Create object from userId object from DB
        self.user_id = user_id
        print(self.user_id)
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
        if selected == "Back":
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
        _ = system('cls||clear')

    def admin_options(self):
        Admin.clear()
        self.print_welcome()
        selected = util.user_select("Please choose one of the options below.", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def log_out(self):
        del self.state_gen

    def manage_gp(self):
        Admin.clear()
        ui.info_section(ui.blue, 'Manage GP Menu')

        # show GPs in system
        self.db = db.Database()
        gp_acct_query = f"SELECT userID, firstname, lastName, email, is_active FROM users WHERE accountType = 'gp'"
        gp_acct_result = self.db.fetch_data(gp_acct_query)
        self.db.close_db()
        gp_dataframe_header = ['ID', 'First Name', 'Last Name', 'email', 'Active?']
        gp_dataframe = DataFrame(gp_acct_result)
        gp_dataframe.columns = gp_dataframe_header
        gp_table = tabulate(gp_dataframe, headers='keys', tablefmt='grid', showindex=False)
        print(gp_table + "\n")

        # allow admin user to choose desired gp account
        # extract GP IDs
        gp_id_list = gp_dataframe['ID'].tolist()
        gp_id_list.append("Back")
        # Extract GP names
        gp_fname_list = gp_dataframe['First Name'].tolist()
        gp_lname_list = gp_dataframe['Last Name'].tolist()
        gp_name_list = [' '.join(z) for z in zip(gp_fname_list, gp_lname_list)]
        gp_list = ["Dr. " + gp_name for gp_name in gp_name_list]
        gp_list.append("Back")
        # Create dictionary with GP IDs as keys and names as values
        gp_dict = {k: v for k, v in zip(gp_list, gp_id_list)}
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
            else:
                self.handle_state_selection("Manage GP")
        elif gp_id == "Back":
            self.handle_state_selection("Admin Options")

    def edit_gp_account_information(self, gp_id, chosen_gp_table):
        Admin.clear()
        ui.info_section(ui.blue, 'Edit GP account')

        # Refresh chose_gp table
        self.db = db.Database()
        gp_acct_query = f"SELECT userID, firstname, lastName, email, is_active FROM users WHERE accountType = 'gp' " \
                        f"AND userID={gp_id}"
        gp_acct_result = self.db.fetch_data(gp_acct_query)
        self.db.close_db()
        gp_dataframe_header = ['ID', 'First Name', 'Last Name', 'email', 'Active?']
        gp_dataframe = DataFrame(gp_acct_result)
        gp_dataframe.columns = gp_dataframe_header
        chosen_gp_table = tabulate(gp_dataframe, headers='keys', tablefmt='grid', showindex=False)
        print(chosen_gp_table + "\n")

        # control program flow
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

        name_changed_confirm = ui.ask_yes_no("Are you sure you want to change the name for this GP's account "
                                              "to the above?", default=False)
        if not name_changed_confirm:
            self.to_edit_gp_account_information(gp_id, chosen_gp_table)
        else:
            self.db = db.Database()
            self.db.exec_one("""UPDATE Users SET firstname=?,LastName=? WHERE userID=?""",
                             [new_firstname, new_lastname, gp_id])
            self.db.close_db()
            ui.info_section(ui.blue, "")
            ui.info_2(ui.standout, f"Successfully updated GP's name to: {new_firstname} {new_lastname}. "
                                   f"Please wait whilst you are redirected.")
            sleep(3)
            self.to_edit_gp_account_information(gp_id, chosen_gp_table)


    def change_gp_registered_email_address(self, gp_id, chosen_gp_table):
        Admin.clear()
        ui.info_section(ui.blue, "Change GP's email ?")

        change_email = True
        self.db = db.Database()
        email_list = self.db.email_list()
        while change_email:
            regex = '^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$'
            new_email = ui.ask_string("Please enter the GP's new email: ")
            if not re.search(regex, new_email):
                print("Invalid Email. Please try again.")
            elif new_email in email_list:
                print('This email has already been registered. Please try again')
            else:
                new_email = new_email.lower()
                change_email = False
                break

        email_changed_confirm = ui.ask_yes_no("Are you sure you want to change the email for this GP's account "
                                              "to the above?", default=False)
        if not email_changed_confirm:
            self.to_edit_gp_account_information(gp_id, chosen_gp_table)
        else:
            self.db = db.Database()
            self.db.exec_one("""UPDATE Users SET email=? WHERE userID=?""", [new_email, gp_id])
            self.db.close_db()
            ui.info_section(ui.blue, "")
            ui.info_2(ui.standout, f"Successfully updated GP's email. Please wait whilst you are redirected.")
            sleep(3)
            self.to_edit_gp_account_information(gp_id, chosen_gp_table)

    def reset_gp_password(self, gp_id, chosen_gp_table):
        Admin.clear()
        ui.info_section(ui.blue, "Reset GP's password?")
        reset_password_confirm = ui.ask_yes_no("Are you sure you want to reset the password for this account?",
                                               default=False)
        if reset_password_confirm:
            # retrieve GP's current password
            self.db = db.Database()
            old_password_query = f"SELECT password from Users WHERE userID = {gp_id}"
            old_password = self.db.fetch_data(old_password_query)
            old_password = old_password[0]['password']
            self.db.close_db()

            if old_password:
                # password validation
                is_long_enough = False
                while not is_long_enough:
                    # Prompt user for new password
                    new_password = ui.ask_password('Password: ')
                    new_password = new_password.encode('utf-8')
                    # do this if ladder the other way, atm not getting past 1st rung if satisfied
                    if len(new_password) < 5:
                        print("The minimum length for a password is 5 characters. Please try again.")
                    elif bcrypt.checkpw(new_password, old_password):
                        print('Your new password cannot be the same as your old password. Please try again.')
                    else:
                        is_long_enough = True

                # hash password
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(new_password, salt)
                # update password in db
                self.db = db.Database()
                self.db.exec_one("""UPDATE Users SET password=?  WHERE userID=?""", [hashed_password, gp_id])
                self.db.close_db()
                # success notification
                ui.info_section(ui.blue, "")
                ui.info_2(ui.standout, f"Successfully reset GP's password. Please wait whilst you are redirected.")
                sleep(3)
                # redirect
                self.to_edit_gp_account_information(gp_id, chosen_gp_table)
        # if user has change of heart before changing password, redirect
        else:
            self.to_edit_gp_account_information(gp_id, chosen_gp_table)

    def remove_gp_account(self, gp_id):
        Admin.clear()
        ui.info_section(ui.blue, 'Remove GP account?')
        delete_gp_confirm = ui.ask_yes_no("Are you sure you want to permanently remove this GP account?", default=False)
        if delete_gp_confirm:
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
        if deactivate_gp_confirm:
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
        if reactivate_gp_confirm:
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
            confirm_patient()
            selected = util.user_select("Please choose one of the options below.", self.state_gen.get_state_options())
            self.handle_state_selection(selected)
        except:
            print("\nNo patients currently require validation!\nRedirecting...")
            sleep(2)
            self.to_admin_options()

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
                print("No result found, Check if the Birth Date was entered in the correct format: DD-MM-YYYY ")
                sleep(2)
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
                print("No result found, Check if the Name was typed in correctly.")
                sleep(2)
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
        elif selected == "Back":
            self.handle_state_selection("Admin Options")

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
                                   f"Please wait whilst you are redirected.")
            sleep(2)
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
                                   f"Please wait whilst you are redirected.")
            sleep(2)
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
                                   f"Please wait whilst you are redirected.")
            sleep(2)
            Admin.clear()
            self.edit_patient_details()
        elif selected == "Back":
            self.handle_state_selection("Back")

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
            illness = input("Illness: ")
            time_afflicted = input("Time Afflicted: ")
            description = input("Description: ")
            prescribed_medication = input("Prescribed Medication:")
            db1 = Database()

            if row == 1 and ref == "Empty":
                mednr = result[0]['Medical_historyNo']

                db1.exec_one("""UPDATE MedicalHistory SET illness=?,time_afflicted=?,description=?, 
                                prescribed_medication=? WHERE Medical_historyNo=?""",
                             (illness, time_afflicted, description, prescribed_medication, mednr,))
                ui.info_2(ui.standout, f"Medical History was added to the Patients record."
                                       f"Please wait whilst you are redirected.")
                sleep(2)
                self.add_medical_history()
            else:

                db1.exec_one(
                    "INSERT INTO MedicalHistory(userID, illness,time_afflicted,description,prescribed_medication) "
                    "VALUES(?, ?,?, ?,?)",
                    (self.ID, illness, time_afflicted, description, prescribed_medication))
                ui.info_2(ui.standout, f"Medical History was added to the Patients record."
                                       f"Please wait whilst you are redirected.")
                sleep(2)
                self.add_medical_history()
        elif selected == "Back":
            self.handle_state_selection("Back")

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
            col_one_list = df['Medical_historyNo'].tolist()
            x = 1

            if row == 1:

                while x == 1:
                    nr = int(input('Enter the MedicalHistoryNr you would like to delete (see above): '))
                    if nr in col_one_list:

                        db1 = Database()
                        db1.exec_one("""UPDATE MedicalHistory SET illness=?,time_afflicted=?,description=?, 
                                        prescribed_medication=? WHERE Medical_historyNo=?""",
                                     ("Empty", "Empty", "Empty", "Empty", nr,))
                        ui.info_2(ui.standout, f"Selected  Medical History was deleted from the Patients record."
                                               f"Please wait whilst you are redirected.")
                        sleep(2)
                        x = 2
                    else:
                        print("Invalid Input, Please select an a MedicalHistoryNr from the table above:")
                        x = 1

                self.handle_state_selection("Back")
            else:
                while x == 1:
                    nr = int(input('Enter the MedicalHistoryNr you would like to delete (see above): '))
                    if nr in col_one_list:
                        db1 = Database()
                        db1.exec_one("DELETE FROM MedicalHistory WHERE Medical_historyNo=?", (nr,))
                        ui.info_2(ui.standout, f"Selected  Medical History was deleted from the Patients record."
                                               f"Please wait whilst you are redirected.")
                        sleep(2)
                        x = 2
                    else:
                        print("Invalid Input, Please select an a MedicalHistoryNr from the table above:")
                        x = 1
                self.delete_medical_history()
        elif selected == "Back":
            self.handle_state_selection("Back")

    def deactivate_patient_account(self):
        self.display_patient_persrecord()
        ui.info_section(ui.blue, 'Deactivate Personal Account Options')
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())

        if selected == "Deactivate the Patients account":
            db = Database()
            db.exec_one("""UPDATE Users SET is_active=0  WHERE userID=?""", (self.ID,))
            ui.info_2(ui.standout, f"Patients account has been deactivated. "
                                   f"Please wait whilst you are redirected.")
            sleep(2)
            self.deactivate_patient_account()
        elif selected == "Back":
            self.handle_state_selection("Manage Patient Account")

    def reactivate_patient_account(self):
        self.display_patient_persrecord()

        ui.info_section(ui.blue, 'Reactivate Personal Account Options')
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())

        if selected == "Reactivate the Patients account":
            db = Database()
            db.exec_one("""UPDATE Users SET is_active=1  WHERE userID=?""", (self.ID,))
            ui.info_2(ui.standout, f"Patients account has been reactivated. "
                                   f"Please wait whilst you are redirected.")
            sleep(2)
            self.reactivate_patient_account()
        elif selected == "Back":
            self.handle_state_selection("Manage Patient Account")

    def track_performance(self):
        Admin.clear()
        ui.info_section(ui.blue, "Performance metrics")
        selected = util.user_select("Please choose one of the trackable items below.",
                                    self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def gp_metrics(self):
        Admin.clear()
        ui.info_section(ui.blue, "GP metrics")
        # TODO:
        # view all GPs
        # number of appointments booked in past week, in past month, in past year
        # Number of holiday days taken
        # number of specialists in each departments

    def patient_metrics(self):
        Admin.clear()
        ui.info_section(ui.blue, "Patient metrics")
        # TODO:
        # view number of appointments
        # view number of pending registrations
        # view number of cancelled appointments
        # view number of referrals
        # view number of prescriptions

    def prescription_metrics(self):
        Admin.clear()
        ui.info_section(ui.blue, "Prescription metrics")
        # TODO:

    def assign_new_admin(self):
        Admin.clear()
        ui.info_section(ui.blue, "Assign a new Admin user")
        assign_admin_confirm = ui.ask_yes_no("Please confirm if you want to assign a new Admin account?",
                                             default=False)
        if assign_admin_confirm:
            new_fname = ui.ask_string("Please enter the new Admin's first name: ").capitalize()
            new_lname = ui.ask_string("Please enter the new Admin's last name: ").capitalize()
            email_repetition = True
            while email_repetition:
                regex = '^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$'
                new_email = input("Please enter the Admin's new email:")
                if not re.search(regex, new_email):
                    print("Invalid Email. Please try again.")
                else:
                    email_repetition = False

            new_password = ui.ask_password("Please enter a new password: ")
            # encode password
            new_password = new_password.encode('UTF-8')
            # hash password
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(new_password, salt)
            curr_date = datetime.datetime.now()
            format_date = curr_date.strftime("%m/%d/%Y %H:%M:%S")
            is_registered = 1
            is_active = 1

            self.db = db.Database()
            self.db.exec_one("""INSERT INTO users(firstName, lastName, email, password,signUpDate, accountType, 
            is_registered, is_active)
                                VALUES(?,?,?,?,?,?,?,?)""",
                             [new_fname, new_lname, new_email, hashed_password, format_date, "admin", is_registered,
                              is_active])
            self.db.close_db()
            ui.info_2(ui.standout, f"Successfully assigned a new Admin. Please wait whilst you are redirected.")
            sleep(2)
            self.state_gen.change_state("Admin Options")

        else:
            self.state_gen.change_state("Admin Options")


# for testing admin functionality
if __name__ == "__main__":
    Admin(2)
