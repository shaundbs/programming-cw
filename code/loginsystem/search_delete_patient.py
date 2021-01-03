
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
    "Admin options": ["Manage patient", "Manage GP", "Register new GP", "Approve new patient", "Log out"],

    # Manage Patient menu
    "Manage Patient": ["Edit Patient Details", "Add Medical History", "Delete Medical History",
                       "Deactivated Patient Account", "Reactivated Patient Account"
                                                      "Back"],
    "Edit Patient Details": ["Change Patient name", "Change Patient email address", "Back"],
    "Add Medical History": ["Back"],
    "Delete Medical History": ["Back"],
    "Deactivated Patient Account": ["Back"],
    "Deactivate Patient account": ["Back"],
    "Reactivate Patient account": ["Back"],
}


def clear():
    _ = system('clear')


class Admin:

    def __init__(self, user_id):
        # Create object from userId object from DB
        self.user_id = 2

    def select_options(self):
        print('1. Manage Patient Account')
        print('2. Manage GP Account')
        print('3. Register GP')
        print('4. Approve Patient')
        print('9. Log Out')
        Option = int(input('Please choose an option: '))
        return Option

    def select_options_TypeOfSearch(self):
        print('1. Seach Patient with Date of Birth')
        print('2. Search Patient with Name')
        print('9. Return to Menu')
        Option = int(input('Please choose an option: '))
        return Option

    def select_options_Manage_Patient(self):
        print('1. Edit Patients Personal Details')
        print('2. Add to Patients Medical History')
        print('3. Delete Patients Medical History')
        print('4. Deactivate Patients Account')
        print('5. Reactivate Patients Account')
        print('9. Return to Menu')
        Option = int(input('Please choose an option: '))
        return Option

    def SearchDoB(self):
        DoB = input("Enter the Date of Birth: ")
        db = Database()
        Index= ["ID","First Name", "Last Name", "DateOfBirth", "email", "Role", "Registered", "Active", "Signed UP"]
        db.exec_one("SELECT userID, FirstName, LastName, DateOfBirth, email, accountType, is_registered, is_active, signUpDate  FROM Users WHERE DateOfBirth = ?", (DoB,))
        result = db.c.fetchall()
        df = DataFrame(result)
        df.columns = Index
        print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
        return df

    def SearchByName():
        LastName = input("Last Name: ")
        db = Database()
        Index= ["ID","First Name", "Last Name", "DateOfBirth", "email", "Role", "Registered", "Active", "Signed UP"]
        db.exec_one("SELECT userID, FirstName, LastName, DateOfBirth, email, accountType, is_registered, is_active, signUpDate  FROM Users WHERE LastName=?", (LastName,))
        result = db.c.fetchall()
        df = DataFrame(result)
        df.columns = Index
        print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
        return df


    def SeePatientRecord(self,df):
        ID = int(input("Enter an ID Number from the table above to see a Patients Medical History: "))
        col_one_list = df['ID'].tolist()
        if ID not in col_one_list:
            print("Invalid ID input, Please select an ID from the table below")
            print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
            self.SeePatientRecord(df)
            #Return to original Menu
        else:
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

            df2 = DataFrame(result)
            df2.columns = Index2
            os.system('clear')
            print(colored('Patient Personal Record', 'green', attrs=['bold']))
            print(tabulate(df1, headers='keys', tablefmt='fancy_grid', showindex=False))
            print(colored('Patient Medical History', 'green', attrs=['bold']))
            print(tabulate(df2, headers='keys', tablefmt='fancy_grid', showindex=False))

            return (ID,df1,df2)


    def DeactivatePatient(self,ID):
        print('1. Deactivate the Patient Account.')
        print('9. Return to Menu')
        option = int(input('Please choose an option: '))
        if option ==1:

            db = Database()
            db.exec_one("""UPDATE Users SET is_active=0  WHERE userID=?""", (ID,))
        if option == 9:
            return option

    def ReactivatePatient(self,ID):
        print('1. Reactivate the Patient Account.')
        print('9. Return to Menu')
        option = int(input('Please choose an option: '))
        if option == 1:
            db = Database()
            db.exec_one("""UPDATE Users SET is_active=1  WHERE userID=?""", (ID,))
        elif option == 9:
            return option
        else:
            print("Wrong Input, please try again")


    def DeleteMedicalHistory(self):
        print('1. Delete Medical History')
        print('9. Return to Menu')
        option = int(input('Please choose an option: '))

        if option==1:
            print('1. Enter the Medical History Nr you would like to delete ')
            Nr = int(input('Please choose an option: '))

            db = Database()
            db.exec_one("DELETE FROM MedicalHistory WHERE Medical_historyNo=?",(Nr,))
            self.DeleteMedicalHistory()
        if option == 9:
            return option

    def AddMedicalHistory(self,ID):
        print('1. Add Medical History')
        print('9. Return to Menu')
        option = int(input('Please choose an option: '))

        if option==1:

            illness = input("Illness: ")
            time_afflicted = input("Time Afflicted: ")
            description = input("Description: ")
            prescribed_medication = input("Prescribed Medication:")
            db = Database()
            db.exec_one("INSERT INTO MedicalHistory(userID, illness,time_afflicted,description,prescribed_medication) VALUES(?, ?,?, ?,?)", (ID,illness,time_afflicted,description,prescribed_medication))
            self.AddMedicalHistory(ID)

        if option == 3:
            return option





    def UpdatePatientDetails(self,ID):
        print('1. Edit Patients Name')
        print('2. Edit Patients Date of Birth')
        print('3. Edit Patients Email')
        print('9. Return to Patient Record')
        option = int(input('Please choose an option: '))


        if option==1:
            FirstName = input("Enter the new First Name: ")
            LastName = input("Enter the new Last Name: ")
            db = Database()
            db.exec_one("""UPDATE Users SET FirstName=?,LastName=?  WHERE userID=?""", (FirstName,LastName,ID,))
            print("Successfully Updated Name,Wait 2 Seconds")
            sleep(2)
            clear()
            self.UpdatePatientDetails(ID)
        if option==2:
            DoB = input("Enter the New Date of Birth: ")
            db = Database()
            db.exec_one("""UPDATE Users SET DateOfBirth=?  WHERE userID=?""", (DoB,ID,))
            print("Successfully Updated Date of Birth, Wait 2 Seconds")
            sleep(2)
            clear()
            self.UpdatePatientDetails(ID)

        if option==3:
            email = input("Enter the New email: ")
            db = Database()
            db.exec_one("""UPDATE Users SET email=?  WHERE userID=?""", (email,ID,))
            print("Successfully Updated Email. Wait 2 Seconds")
            sleep(2)
            clear()
            self.UpdatePatientDetails(ID)

        if option==9:
            return option







    def main(self):
        Loggin = True
        while Loggin == True:
            Option=self.select_options()
            if Option==1:
                os.system('clear')
                SearchOption=self.select_options_TypeOfSearch()
                if SearchOption==1:
                    os.system('clear')
                    dataframe=self.SearchDoB()
                if SearchOption==2:
                    os.system('clear')
                    dataframe=self.SearchByName()
                if SearchOption==3:
                    self.main()



                Patient_Record=self.SeePatientRecord(dataframe)
                Option=self.select_options_Manage_Patient()

                if Option==1:
                    os.system('clear')
                    print(tabulate(Patient_Record[1], headers='keys', tablefmt='fancy_grid', showindex=False))
                    option = self.UpdatePatientDetails(Patient_Record[0])
                    print("Updating Patient Details Completed, Wait 2 seconds...")
                    sleep(2)
                    os.system('clear')
                    if option == 9:
                        main()

                if Option== 2:
                    os.system('clear')
                    print(colored('Patient Personal Record', 'green', attrs=['bold']))
                    print(tabulate(Patient_Record[1], headers='keys', tablefmt='fancy_grid', showindex=False))
                    print(colored('Patient Medical History', 'green', attrs=['bold']))
                    print(tabulate(Patient_Record[2], headers='keys', tablefmt='fancy_grid', showindex=False))
                    Option = self.AddMedicalHistory(Patient_Record[0])
                    print("New Medical History was added to Patients Record, Wait 2 seconds....")
                    sleep(2)
                    os.system('clear')
                    if Option == 9:
                        self.main()



                if Option == 3:
                    os.system('clear')
                    print(colored('Patient Personal Record', 'green', attrs=['bold']))
                    print(tabulate(Patient_Record[1], headers='keys', tablefmt='fancy_grid', showindex=False))
                    print(colored('Patient Medical History', 'green', attrs=['bold']))
                    print(tabulate(Patient_Record[2], headers='keys', tablefmt='fancy_grid', showindex=False))
                    print("Updating Patient Details Completed, Wait 2 seconds")
                    Option = self.DeleteMedicalHistory()
                    print("Medical History was deleted from Patients Record, Wait 2 seconds")
                    sleep(2)
                    os.system('clear')
                    if Option == 9:
                        self.main()

                if Option==4:
                    os.system('clear')
                    print(colored('Patient Medical History', 'green', attrs=['bold']))
                    print(tabulate(Patient_Record[1], headers='keys', tablefmt='fancy_grid', showindex=False))
                    self.DeactivatePatient(Patient_Record[0])
                    print("Patient Account has been deactivated, Wait 2 seconds")
                    sleep(2)
                    os.system('clear')

                if  Option==5:
                    os.system('clear')
                    print(colored('Patient Medical History', 'green', attrs=['bold']))
                    print(tabulate(Patient_Record[1], headers='keys', tablefmt='fancy_grid', showindex=False))
                    self.ReactivatePatient(Patient_Record[0])
                    print("Patient Account has been reactivated, Wait 2 seconds")
                    sleep(2)
                    os.system('clear')

                if Option == 9:
                    os.system('clear')
                    self.main()







Admin("12").main()

if Nr in col_one_list:
    db1 = Database()
db1.exec_one("""UPDATE MedicalHistory SET illness=?,time_afflicted=?,description=?, 
                                                                prescribed_medication=? WHERE Medical_historyNo=?""",
             ("Empty", "Empty", "Empty", "Empty", Nr,))
x = 2
else:
print("Invalid Input, Please select an a MedicalHistoryNr from the table above:")

x = 1
