
from panel import Panel, Database
from pandas import DataFrame
from os import system
import os
from time import sleep

from tabulate import tabulate
from termcolor import colored


def clear():

        _ = system('clear')

def select_options():
    print('1. Search Patient')
    print('2. Search GP')
    print('3. Register GP')
    print('4. Approve Patient')
    print('9. Log Out')
    option = int(input('Please choose an option: '))
    return option

def select_options_TypeOfSearch():
    print('1. Seach Patient with Date of Birth')
    print('2. Search Patient with Name')
    print('9. Return to Menu')
    option = int(input('Please choose an option: '))
    return option

def SearchDoB():
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
    FirstName = input("First Name: ")
    LastName = input("Last Name: ")
    db = Database()
    Index= ["ID","First Name", "Last Name", "DateOfBirth", "email", "Role", "Registered", "Active", "Signed UP"]
    db.exec_one("SELECT userID, FirstName, LastName, DateOfBirth, email, accountType, is_registered, is_active, signUpDate  FROM Users WHERE FirstName = ? and LastName=?", (FirstName,LastName,))
    result = db.c.fetchall()
    df = DataFrame(result)
    df.columns = Index
    print(df)
    return df


def SeePatientRecord(df):
    ID = int(input("Enter an ID Number from the table above to see a Patients Medical History: "))
    col_one_list = df['ID'].tolist()
    if ID not in col_one_list:
        print("Invalid ID input, Please select an ID from the table below")
        print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
        SeePatientRecord(df)
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

        print(colored('Patient Personal Record', 'green', attrs=['bold']))
        print(tabulate(df1, headers='keys', tablefmt='fancy_grid', showindex=False))
        print(colored('Patient Medical History', 'green', attrs=['bold']))
        print(tabulate(df2, headers='keys', tablefmt='fancy_grid', showindex=False))

        print('1. Edit Patients Personal Details')
        print('2. Add to Patients Medical History')
        print('3. Delete Patients Medical History')
        print('4. Deactivate Patients Account')
        print('5. Reactivate Patients Account')
        print('9. Return to Menu')

        option = int(input('Please choose an option: '))
        return (option,ID,df1,df2)


def DeactivatePatient(ID):
    print('1. Deactivate the Patient Account.')
    print('9. Return to Menu')
    option = int(input('Please choose an option: '))
    if option ==1:

        db = Database()
        db.exec_one("""UPDATE Users SET is_active=0  WHERE userID=?""", (ID,))
    if option == 9:
        return option

def ReactivatePatient(ID):
    print('1. Reactivate the Patient Account.')
    print('9. Return to Menu')
    option = int(input('Please choose an option: '))
    if option == 1:
        db = Database()
        db.exec_one("""UPDATE Users SET is_active=1  WHERE userID=?""", (ID,))
    if option == 9:
        return option

def DeleteMedicalHistory():
    print('1. Delete Medical History')
    print('9. Return to Menu')
    option = int(input('Please choose an option: '))

    if option==1:
        print('1. Enter the Medical History Nr you would like to delete ')
        Nr = int(input('Please choose an option: '))

        db = Database()
        db.exec_one("DELETE FROM MedicalHistory WHERE Medical_historyNo=?",(Nr,))
        DeleteMedicalHistory()
    if option == 9:
        return option

def AddMedicalHistory(ID):
    print('1. Add Medical History')
    print('9. Return to Menu')
    option = int(input('Please choose an option: '))

    if option==1:

        illness = input("illness: ")
        time_afflicted = input("time afflicted: ")
        description = input("time afflicted: ")
        prescribed_medication = input("prescribed medication:")
        db = Database()
        db.exec_one("INSERT INTO MedicalHistory(userID, illness,time_afflicted,description,prescribed_medication) VALUES(?, ?,?, ?,?)", (ID,illness,time_afflicted,description,prescribed_medication))
        AddMedicalHistory(ID)

    if option == 3:


        return option





def UpdatePatientDetails(ID):
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
        UpdatePatientDetails(ID)
    if option==2:
        DoB = input("Enter the New Date of Birth: ")
        db = Database()
        db.exec_one("""UPDATE Users SET DateOfBirth=?  WHERE userID=?""", (DoB,ID,))
        print("Successfully Updated Date of Birth, Wait 2 Seconds")
        sleep(2)
        clear()
        UpdatePatientDetails(ID)

    if option==3:
        email = input("Enter the New email: ")
        db = Database()
        db.exec_one("""UPDATE Users SET email=?  WHERE userID=?""", (email,ID,))
        print("Successfully Updated Email. Wait 2 Seconds")
        sleep(2)
        clear()
        UpdatePatientDetails(ID)

    if option==9:
        return option







def MainSearchPatient():
    Loggin = True
    while Loggin == True:
        Option=select_options()
        if Option==1:
            os.system('clear')
            SearchOption=select_options_TypeOfSearch()
            if SearchOption==1:
                os.system('clear')
                dataframe=SearchDoB()
            if SearchOption==2:
                os.system('clear')
                dataframe=SearchByName()
            PatientRecordOption=SeePatientRecord(dataframe)


            if PatientRecordOption[0]==1:
                os.system('clear')
                print(tabulate(PatientRecordOption[2], headers='keys', tablefmt='fancy_grid', showindex=False))
                option=UpdatePatientDetails(PatientRecordOption[1])
                print("Updating Patient Details Completed, Wait 2 seconds")
                sleep(2)
                clear()
                if option == 9:
                    main()


            if PatientRecordOption[0]==2:
                os.system('clear')
                print(colored('Patient Personal Record', 'green', attrs=['bold']))
                print(tabulate(PatientRecordOption[2], headers='keys', tablefmt='fancy_grid', showindex=False))
                print(colored('Patient Medical History', 'green', attrs=['bold']))
                print(tabulate(PatientRecordOption[3], headers='keys', tablefmt='fancy_grid', showindex=False))
                option= AddMedicalHistory(PatientRecordOption[1])
                print("New Medical History was added to Patients Record, Wait 2 seconds")
                sleep(2)
                clear()
                if option==9:
                    main()

            if PatientRecordOption[0]==3:
                os.system('clear')
                print(colored('Patient Personal Record', 'green', attrs=['bold']))
                print(tabulate(PatientRecordOption[2], headers='keys', tablefmt='fancy_grid', showindex=False))
                print(colored('Patient Medical History', 'green', attrs=['bold']))
                print(tabulate(PatientRecordOption[3], headers='keys', tablefmt='fancy_grid', showindex=False))
                print("Updating Patient Details Completed, Wait 2 seconds")
                option = DeleteMedicalHistory()
                print("Medical History was deleted from Patients Record, Wait 2 seconds")
                sleep(2)
                clear()
                if option == 9:
                    main()

            if PatientRecordOption[0]==4:
                os.system('clear')
                print(colored('Patient Medical History', 'green', attrs=['bold']))
                print(tabulate(PatientRecordOption[2], headers='keys', tablefmt='fancy_grid', showindex=False))
                DeactivatePatient(PatientRecordOption[1])
                print("Patient Account has been deactivated, Wait 2 seconds")
                sleep(2)
                clear()


            if PatientRecordOption[0]==5:
                os.system('clear')
                print(colored('Patient Medical History', 'green', attrs=['bold']))
                print(tabulate(PatientRecordOption[2], headers='keys', tablefmt='fancy_grid', showindex=False))
                ReactivatePatient(PatientRecordOption[1])
                print("Patient Account has been reactivated, Wait 2 seconds")
                sleep(2)
                clear()

            if PatientRecordOption[0]==9:
                os.system('clear')
                main()

        if Option == 9:
            Loggin = False


MainSearchPatient()





