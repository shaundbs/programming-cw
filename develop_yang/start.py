import sqlite3
import bcrypt
import getpass  # hide password when inputting

# Welcome Page.
print('Welcome')
print('1. Login')
print('2. Register')
option = int(input('Your option:'))

# Redirects to login or register.
if option == 1:
    # User input.
    fName = input('Fist Name:')
    lName = input('Last Name:')
    pWord = getpass.getpass('Password:')

    # Connect to db and fetch data.
    connection = sqlite3.connect('test1.db')
    c = connection.cursor()
    a = (fName, lName,)
    c.execute(
        "SELECT password FROM Patients WHERE firstName = ? and lastName = ?", a)
    record = c.fetchone()[0]
    connection.commit()
    connection.close()

    # Verify data.
    pWord = pWord.encode('utf-8')
    if bcrypt.checkpw(pWord, record):
        # TODO: move on to features.
        print(True)
    else:
        # TODO: exit program.
        print(False)


elif option == 2:
    # User input.
    # TODO: data validation.
    fName = input('Fist Name:')
    lName = input('Last Name:')
    pWord = getpass.getpass('Password:')

    # Encode pw and insert user credentials into db.
    pWord = pWord.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pWord, salt)

    connection = sqlite3.connect('test1.db')
    c = connection.cursor()
    a = [(fName, lName, hashed), ]
    c.executemany("INSERT INTO Patients Values (?,?,?)", a)
    connection.commit()
    connection.close()

else:
    print('Wrong Input.')
