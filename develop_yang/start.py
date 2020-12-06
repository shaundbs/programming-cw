import sqlite3
import bcrypt
import getpass  # hide password when inputting

# Welcome Page.
print('Welcome')

# Redirects to login or register.
tries_flag = ""
while tries_flag != "Close the program":
    print("-----------------------------------------")
    print("|Enter 1 for Admin mode			|\n|Enter 2 for Patient mode	        |\n|Enter 3 for GP mode			|")
    print("-----------------------------------------")
    Admin_user_mode = input("Enter your mode : ")

    if Admin_user_mode == "1":
        print('Not Available yet.')
        break

    elif Admin_user_mode == "2":
        print('1. Login')
        print('2. Register')
        option = int(input('Your option:'))
        if option == 1:
            # Login. User input.
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
            # Register. User input.
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

    elif Admin_user_mode == "3":
        print('Not Available yet.')
        break

    else:
        print("Please choice just 1 or 2 or 3")
