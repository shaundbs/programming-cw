
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