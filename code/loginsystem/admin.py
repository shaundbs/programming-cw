
from panel import Panel, Database
from pandas import DataFrame
from os import system
import os
from time import sleep
import cli_ui as ui
import gp_utilities as util
from termcolor import colored
from tabulate import tabulate
from state_gen import StateGenerator

states = {
    # admin menu
    "Admin Options": ["Manage Patient", "Manage GP", "Register new GP", "Approve new patient", "Log out"],
    "Manage Patient": ["Search by Date of Birth", "Search by Last Name", "Back",],
    "Search by Date of Birth": ["Manage Patient Account"],
    "Search by Last Name": ["Manage Patient Account"],


    # Manage Patient menu
    "Manage Patient Account": ["Edit Patient Details", "Add Medical History", "Delete Medical History",
                               "Deactivated Patient Account", "Reactivated Patient Account","Back"],
    "Edit Patient Details": ["Change Patient name", "Change Date of Birth","Change Patient email address", "Back"],
    "Add Medical History": ["Add to the Medical History","Back"],
    "Delete Medical History": ["Delete Medical History","Back"],
    "Deactivate Patient Account": [ "Deactivate the Patients account","Back"],
    "Reactivate Patient Account":  [ "Reactivate the Patients account","Back"],
}

class Admin:

    def __init__(self, user_id):
        # Create object from userId object from DB
        self.user_id = user_id

        # Get firstname and lastname of admin user
        self.db = Database()
        self.db.exec_one("SELECT userID, FirstName, LastName FROM Users WHERE userID = ?",(self.user_id,))
        result = self.db.c.fetchall()
        df_result = DataFrame(result)
        self.firstname, self.lastname = df_result.loc[0][1], df_result.loc[0][2]

        # initialise state machine
        self.state_gen = StateGenerator(state_dict=states, state_object=self)
        self.state_gen.change_state("admin options")

    def admin_options(self):
        Admin.clear()
        self.print_welcome()
        selected = util.user_select("Please choose one of the options above.", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def print_welcome(self):
        ui.info_section(ui.blue, 'Welcome to the GP Dashboard')
        print(f"Hi, Welcome to the Admin Page:  {self.firstname}")

    def handle_state_selection(self, selected):
        if selected == 'Back':
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

        Index1= ["UserID","First Name", "Last Name", "DateOfBirth", "email", "Role", "Registered", "Active", "Signed UP"]
        Index2=["MedicalHistoryID","UserID","illness", "time_afflicted", "description", "prescribed_medication"]
        db1 = Database()
        db1.exec_one( "SELECT userID, FirstName, LastName, DateOfBirth, email, accountType, is_registered, is_active, signUpDate  FROM Users WHERE userID = ?",
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
            "SELECT userID, FirstName, LastName, DateOfBirth, email, accountType, is_registered, is_active, signUpDate  FROM Users WHERE userID = ?",
            (self.ID,))
        result = db1.c.fetchall()
        Index1 = ["UserID", "First Name", "Last Name", "DateOfBirth", "email", "Role", "Registered", "Active",
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
            "SELECT userID, FirstName, LastName, DateOfBirth, email, accountType, is_registered, is_active, signUpDate  FROM Users WHERE userID = ?",
            (self.ID,))
        result = db1.c.fetchall()
        Index1 = ["UserID", "First Name", "Last Name", "DateOfBirth", "email", "Role", "Registered", "Active",
                  "Signed UP"]
        df1 = DataFrame(result)
        df1.columns = Index1

        print(colored('Patient Personal Record', 'green', attrs=['bold']))
        print(tabulate(df1, headers='keys', tablefmt='fancy_grid', showindex=False))

    def log_out(self):
        # TODO
        pass

    def manage_patient(self):

        os.system('clear')

        ui.info_section(ui.blue, 'Manage Patient Options')
        selected = util.user_select("Please choose an option: ", self.state_gen.get_state_options())

        if selected == None:
            self.handle_state_selection("Manage Patient")

        if selected=="Search by Date of Birth":
            DoB = input("Enter the Date of Birth  (Format: DD-MM-YYYY EXAMPLE: 22-05-1995): ")
            db = Database()
            Index = ["ID", "First Name", "Last Name", "DateOfBirth", "email", "Role", "Registered", "Active",
                     "Signed UP"]
            db.exec_one(
                "SELECT userID, FirstName, LastName, DateOfBirth, email, accountType, is_registered, is_active, signUpDate  FROM Users WHERE DateOfBirth = ?",
                (DoB,))
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
            Index = ["ID", "First Name", "Last Name", "DateOfBirth", "email", "Role", "Registered", "Active",
                     "Signed UP"]
            db.exec_one(
                "SELECT userID, FirstName, LastName, DateOfBirth, email, accountType, is_registered, is_active, signUpDate  FROM Users WHERE LastName = ?",
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
        elif selected=="Deactivated Patient Account":
            self.to_deactivate_patient_account()
        elif selected=="Reactivated Patient Account":
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
            print("Successfully Updated Name,Wait 2 Seconds")
            sleep(2)
            Admin.clear()
            self.edit_patient_details()
        elif selected=="Change Date of Birth":
            DoB = input("Enter the New Date of Birth: ")
            db = Database()
            db.exec_one("""UPDATE Users SET DateOfBirth=?  WHERE userID=?""", (DoB,self.ID,))
            print("Successfully Updated Date of Birth, Wait 2 Seconds")
            sleep(2)
            Admin.clear()
            self.edit_patient_details()

        elif selected=="Change Patient email address":
            email = input("Enter the New email : ")
            db = Database()
            db.exec_one("""UPDATE Users SET email=?  WHERE userID=?""", (email,self.ID,))
            print("Successfully Updated Date of Birth, Wait 2 Seconds")
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
            Ref = result[0][2]
            illness = input("Illness: ")
            time_afflicted = input("Time Afflicted: ")
            description = input("Description: ")
            prescribed_medication = input("Prescribed Medication:")
            db1 = Database()

            if row == 1 and Ref=="Empty":
                MedNr = result[0][0]

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
            col_one_list = df.loc[:][0].tolist()
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

Admin(2)