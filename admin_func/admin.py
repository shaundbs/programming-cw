import os
from os import system
from time import sleep
import re
from . import admin_database as db
from . import admin_utilities as util
import bcrypt
import cli_ui as ui
from .admin_database import Database
from .confirmPatient import confirm_patient, validate
from pandas import DataFrame
from .registerGP import registerGP, confirmation
from tabulate import tabulate
from termcolor import colored

from state_manager import StateGenerator

states = {
    # admin menu
    "Admin options": ["Manage patient", "Manage GP", "Register new GP", "Approve new patients", "Assign new admin", "Track Performance", "Log out"],
    "Return to menu": ["Manage patient", "Manage GP", "Register new GP", "Approve new patients", "Assign new admin", "Track Performance", "Log out"],
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
    "Approve new patients": ["Continue validation", "Back"],
    "Continue validation": ["Validate more entries", "Return to menu"],
    "Validate more entries": ["Continue validation", "Return to menu"],

    # Manage Patient menu
    "Manage Patient Account": ["Edit Patient Details", "Add Medical History", "Delete Medical History",
                               "Deactivate Patient Account", "Reactivate Patient Account","Back"],
    "Edit Patient Details": ["Change Patient name", "Change Date of Birth","Change Patient email address", "Back"],
    "Add Medical History": ["Add to the Medical History","Back"],
    "Delete Medical History": ["Delete Medical History","Back"],
    "Deactivate Patient Account": [ "Deactivate the Patients account","Back"],
    "Reactivate Patient Account":  [ "Reactivate the Patients account","Back"],


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
        if selected == "Back":
            self.state_gen.call_parent_state()
        else:
            self.state_gen.change_state(selected)

    def state_selection_with_argument(self, selected, arg):
        selected = selected.lower().replace(" ", "_")
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
        change_name_confirm = ui.ask_yes_no("Are you sure you want to change the name of this GP's account?",
                                            default=False)
        if change_name_confirm == True:
            new_fName = ui.ask_string("Please enter the GP's new first name: ").capitalize()
            new_lName = ui.ask_string("Please enter the GP's new last name: ").capitalize()
            self.db = db.Database()
            self.db.exec_one("""UPDATE Users SET FirstName=?,LastName=? WHERE userID=?""",
                             [new_fName, new_lName, gp_id])
            self.db.close_db()
            # ui.info_2(ui.standout, f"This account's name has been changed to: {new_fName} {new_lName}")
            self.state_gen.change_state("Manage GP")
        else:
            self.handle_state_selection("Manage GP")

    def change_gp_registered_email_address(self, gp_id):
        Admin.clear()
        ui.info_section(ui.blue, "Change GP's email ?")
        change_email_confirm = ui.ask_yes_no("Are you sure you want to change the email for this GP's account?",
                                             default=False)
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
        reset_password_confirm = ui.ask_yes_no("Are you sure you want to reset the password for this account?",
                                               default=False)
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
            confirm_patient()
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

        
# manage patient functionality
    @staticmethod
    def SeePatientRecord(df):
        x=1
        while x==1:
            ID = int(input("Enter an ID Number from the table above to see a Patients Medical History: "))
            col_one_list = df['ID'].tolist()
            if ID not in col_one_list:
                print("Invalid ID input, Please select an ID from the table below")
                x=1
                #Return to original Menu
            else:
                x+=1

        Index1= ["UserID","First Name", "Last Name", "date_of_birth", "email", "Role", "Registered", "Active", "Signed UP"]
        Index2=["MedicalHistoryID","UserID","illness", "time_afflicted", "description", "prescribed_medication"]
        db1 = Database()
        db1.exec_one( "SELECT userID, FirstName, LastName, date_of_birth, email, accountType, is_registered, is_active, signUpDate  FROM Users WHERE userID = ?",
            (ID,))
        result = db1.c.fetchall()
        df1 = DataFrame(result)
        df1.columns = Index1
        db2 = Database()
        db2.exec_one( "SELECT Medical_historyNo, userID, illness , time_afflicted, description, prescribed_medication FROM MedicalHistory WHERE userID = ?",
            (ID,))
        result = db2.c.fetchall()
        row=len(result)
        print(row)

        if row==0:

            db2.exec_one(
                "INSERT INTO MedicalHistory(userID, illness,time_afflicted,description,prescribed_medication) VALUES(?, ?,?, ?,?)",
                (ID, "Empty", "Empty", "Empty", "Empty"))
            db2.exec_one(
                "SELECT Medical_historyNo, userID, illness , time_afflicted, description, prescribed_medication FROM MedicalHistory WHERE userID = ?",
                (ID,))
            result = db2.c.fetchall()
            df2 = DataFrame(result)
            df2.columns = Index2
            return (ID, df1, df2)


        else:
            df2 = DataFrame(result)
            df2.columns = Index2
            return (ID,df1,df2)

    def display_patient_record(self):
        Admin.clear()
        db1 = Database()
        db1.exec_one(
            "SELECT userID, FirstName, LastName, date_of_birth, email, accountType, is_registered, is_active, signUpDate  FROM Users WHERE userID = ?",
            (self.ID,))
        result = db1.c.fetchall()
        Index1 = ["UserID", "First Name", "Last Name", "date_of_birth", "email", "Role", "Registered", "Active",
                  "Signed UP"]
        df1 = DataFrame(result)
        df1.columns = Index1

        db2 = Database()
        db2.exec_one(
            "SELECT Medical_historyNo, userID, illness , time_afflicted, description, prescribed_medication FROM MedicalHistory WHERE userID = ?",
            (self.ID,))
        result = db2.c.fetchall()
        Index2 = ["MedicalHistoryID", "UserID", "illness", "time_afflicted", "description", "prescribed_medication"]
        df2 = DataFrame(result)
        df2.columns = Index2

        print(colored('Patient Personal Record', 'green', attrs=['bold']))
        print(tabulate(df1, headers='keys', tablefmt='fancy_grid', showindex=False))
        print(colored('Patient Medical History', 'green', attrs=['bold']))
        print(tabulate(df2, headers='keys', tablefmt='fancy_grid', showindex=False))

    def display_patient_PersRecord(self):
        Admin.clear()
        db1 = Database()
        db1.exec_one(
            "SELECT userID, FirstName, LastName, date_of_birth, email, accountType, is_registered, is_active, signUpDate  FROM Users WHERE userID = ?",
            (self.ID,))
        result = db1.c.fetchall()
        Index1 = ["UserID", "First Name", "Last Name", "date_of_birth", "email", "Role", "Registered", "Active",
                  "Signed UP"]
        df1 = DataFrame(result)
        df1.columns = Index1

        print(colored('Patient Personal Record', 'green', attrs=['bold']))
        print(tabulate(df1, headers='keys', tablefmt='fancy_grid', showindex=False))

    def manage_patient(self):

        os.system('clear')

        ui.info_section(ui.blue, 'Manage Patient Options')
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())

        if selected == None:
            self.handle_state_selection("Manage Patient")

        if selected=="Search by Date of Birth":
            DoB = input("Enter the Date of Birth  (Format: YYYY-MM-DD EXAMPLE: 1996-10-16): ")
            db = Database()
            Index = ["ID", "First Name", "Last Name", "date_of_birth", "email", "Role", "Registered", "Active",
                     "Signed UP"]
            db.exec_one(
                "SELECT userID, FirstName, LastName, date_of_birth, email, accountType, is_registered, is_active, signUpDate  FROM Users WHERE date_of_birth = ? and accountType=? ",
                (DoB,'patient'))
            result = db.c.fetchall()
            row=len(result)
            if row ==0:
                print("No result found, Check if the Birth Date was entered in the correct format: DD-MM-YYYY ")
                sleep(2)
                Admin.clear()
                self.to_manage_patient()

            else:
                df = DataFrame(result)
                df.columns = Index
                print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
                SeePatientRecord=self.SeePatientRecord(df)
                self.ID=SeePatientRecord[0]
                self.DF1=SeePatientRecord[1]
                self.DF2 = SeePatientRecord[2]
                self.to_manage_patient_account()
        elif selected=="Search by Last Name":
            Name = input("Enter the Last Name of the Patient: ")
            db = Database()
            Index = ["ID", "First Name", "Last Name", "date_of_birth", "email", "Role", "Registered", "Active",
                     "Signed UP"]
            db.exec_one(
                "SELECT userID, FirstName, LastName, date_of_birth, email, accountType, is_registered, is_active, signUpDate  FROM Users WHERE LastName = ?",
                (Name,))
            result = db.c.fetchall()
            row=len(result)
            if row ==0:
                print("No result found, Check if the Name was typed in correctly.")
                sleep(2)
                Admin.clear()
                self.to_manage_patient()
            else:
                df = DataFrame(result)
                df.columns = Index
                print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
                SeePatientRecord=Admin.SeePatientRecord(df)
                self.ID=SeePatientRecord[0]
                self.DF1=SeePatientRecord[1]
                self.DF2 = SeePatientRecord[2]
                self.to_manage_patient_account()
        elif selected=="Back":
            self.handle_state_selection("Admin Options")

    def manage_patient_account(self):
        self.display_patient_record()
        ui.info_section(ui.blue, 'Manage Patient Account Options')
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())
        if selected=="Edit Patient Details":
            self.to_edit_patient_details()
        elif selected=="Add Medical History":
            self.to_add_medical_history()
        elif selected=="Delete Medical History":
            self.to_delete_medical_history()
        elif selected=="Deactivate Patient Account":
            self.to_deactivate_patient_account()
        elif selected=="Reactivate Patient Account":
            self.to_reactivate_patient_account()
        elif selected=="Back":
            self.handle_state_selection("Admin Options")

    def edit_patient_details(self):
        self.display_patient_PersRecord()
        ui.info_section(ui.blue, 'Edit Patient Personal Account Options')
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())

        if selected=="Change Patient name":
            FirstName = input("Enter the new First Name: ")
            LastName = input("Enter the new Last Name: ")
            db = Database()
            db.exec_one("""UPDATE Users SET FirstName=?,LastName=?  WHERE userID=?""", (FirstName,LastName,self.ID,))
            print("Successfully Updated Patient Name,Wait 2 Seconds")
            sleep(2)
            Admin.clear()
            self.edit_patient_details()
        elif selected=="Change Date of Birth":
            DoB = util.get_user_date()
            db = Database()
            db.exec_one("""UPDATE Users SET date_of_birth=?  WHERE userID=?""", (DoB,self.ID,))
            print("Successfully Updated Date of Birth, Wait 2 Seconds")
            sleep(2)
            Admin.clear()
            self.edit_patient_details()

        elif selected=="Change Patient email address":
            email_repetition=True
            while email_repetition:
                regex = '^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$'
                email = input('Email:')
                if not re.search(regex, email):
                    print("Invalid Email. Please try again.")
                else:
                    email_repetition = False

            db = Database()
            db.exec_one("""UPDATE Users SET email=?  WHERE userID=?""", (email,self.ID,))
            print("Successfully Updated the email, Wait 2 Seconds")
            sleep(2)
            Admin.clear()
            self.edit_patient_details()
        elif selected=="Back":
            self.handle_state_selection("Back")

    def add_medical_history(self):
        self.display_patient_record()
        ui.info_section(ui.blue, 'Add Medical History')
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())

        if selected == "Add to the Medical History":

            db1 = Database()
            db1.exec_one(
                "SELECT Medical_historyNo, userID, illness , time_afflicted, description, prescribed_medication FROM MedicalHistory WHERE userID = ?",
                (self.ID,))
            result = db1.c.fetchall()
            row=len(result)
            Ref = result[0]['illness']
            illness = input("Illness: ")
            time_afflicted = input("Time Afflicted: ")
            description = input("Description: ")
            prescribed_medication = input("Prescribed Medication:")
            db1 = Database()

            if row == 1 and Ref=="Empty":
                MedNr =  result[0]['Medical_historyNo']

                db1.exec_one("""UPDATE MedicalHistory SET illness=?,time_afflicted=?,description=?, 
                                                                      prescribed_medication=? WHERE Medical_historyNo=?""",
                             (illness, time_afflicted, description, prescribed_medication, MedNr,))
                self.add_medical_history()
            else:


                db1.exec_one(
                    "INSERT INTO MedicalHistory(userID, illness,time_afflicted,description,prescribed_medication) VALUES(?, ?,?, ?,?)",
                    (self.ID, illness, time_afflicted, description, prescribed_medication))
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
                "SELECT Medical_historyNo, userID, illness , time_afflicted, description, prescribed_medication FROM MedicalHistory WHERE userID = ?",
                (self.ID,))
            result = db1.c.fetchall()
            row=len(result)
            df=DataFrame(result)
            col_one_list = df['Medical_historyNo'].tolist()
            x=1

            if row ==1:

                while x==1:
                    Nr = int(input('Enter the MedicalHistoryNr you would like to delete (see above): '))
                    if Nr in col_one_list:

                        db1=Database()
                        db1.exec_one("""UPDATE MedicalHistory SET illness=?,time_afflicted=?,description=?, 
                                                                              prescribed_medication=? WHERE Medical_historyNo=?""",
                                     ("Empty", "Empty", "Empty", "Empty", Nr,))
                        x=2
                    else:
                        print("Invalid Input, Please select an a MedicalHistoryNr from the table above:")
                        x=1

                self.handle_state_selection("Back")
            else:
                while x == 1:
                    Nr = int(input('Enter the MedicalHistoryNr you would like to delete (see above): '))
                    if Nr in col_one_list:
                        db1 = Database()
                        db1.exec_one("DELETE FROM MedicalHistory WHERE Medical_historyNo=?", (Nr,))
                        x=2
                    else:
                        print("Invalid Input, Please select an a MedicalHistoryNr from the table above:")
                        x = 1
                self.delete_medical_history()
        elif selected== "Back":
            self.handle_state_selection("Back")

    def deactivate_patient_account(self):
        self.display_patient_PersRecord()
        ui.info_section(ui.blue, 'Deactivate Personal Account Options')
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())

        if selected=="Deactivate the Patients account":
            db = Database()
            db.exec_one("""UPDATE Users SET is_active=0  WHERE userID=?""", (self.ID,))
            self.deactivate_patient_account()
        elif selected == "Back":
            self.handle_state_selection("Manage Patient Account")

    def reactivate_patient_account(self):
        self.display_patient_PersRecord()

        ui.info_section(ui.blue, 'Reactivate Personal Account Options')
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())

        if selected=="Reactivate the Patients account":
            db = Database()
            db.exec_one("""UPDATE Users SET is_active=1  WHERE userID=?""", (self.ID,))
            self.reactivate_patient_account()
        elif selected == "Back":
            self.handle_state_selection("Manage Patient Account")

    def track_performance(self):
        Admin.clear()
        ui.info_section(ui.blue, "Performance metrics")
        selected = util.user_select("Please choose one of the trackable items below.", self.state_gen.get_state_options())
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
        if assign_admin_confirm == True:
            new_fName = ui.ask_string("Please enter the new Admin's first name: ").capitalize()
            new_lName = ui.ask_string("Please enter the new Admin's last name: ").capitalize()
            new_email = ui.ask_string("Please enter the Admin's new email: ")
            new_password = ui.ask_password("Please enter a new password: ")
            # encode password
            new_password = new_password.encode('UTF-8')
            # hash password
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(new_password, salt)
            curr_date = datetime.datetime.now()
            format_date = curr_date.strftime("%m-%d-%Y %H:%M")

            self.db = db.Database()
            self.db.exec_one("""INSERT INTO users(firstName, lastName, email, password,signUpDate, accountType)
                                VALUES(?,?,?,?,?,?)""", [new_fName, new_lName, new_email, hashed_password,format_date, "admin"])
            self.db.close_db()
            self.state_gen.change_state("Admin Options")
        else:
            self.state_gen.change_state("Admin Options")

# for testing admin functionality
if __name__ == "__main__":
    Admin(2)
