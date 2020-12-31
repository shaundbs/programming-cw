from patient_func.patient_database import Database
import bcrypt
import getpass

# TODO: WHEN TO CLOSE DB?


class Panel:
    user_type = False
    user_id = 0

    def __init__(self):
        self.db = Database()

    def welcome(self):
        print('Welcome')

    def login(self):
        email = input('Email:')
        pWord = getpass.getpass('Password:')
        a = (email,)
        self.db.exec_one(
            "SELECT password, userId, accountType, is_registered FROM Users WHERE email = ?", a)
        record = self.db.c.fetchone()
        pWord = pWord.encode('utf-8')

        if not record:
            print('Sorry, your account does not exist in the system')
            self.login()

        elif bcrypt.checkpw(pWord, record[0]):
            if record[2] == 'patient':
                if record[3] == 1:
                    return ['patient', record[1]]
                else:
                    print('Sorry, your registration is not approved yet.')
                    return False
            elif record[2] == 'gp':
                return ['gp', record[1]]
            elif record[2] == 'admin':
                return ['admin', record[1]]

        else:
            print('Your password is wrong, Please retry.')
            self.login()

    def user_options(self):
        print("1. Log in")
        print("2. Register")
        print("3. Exit")
        option = input("Enter your option : ")
        return option

    def password_checker(self, pw):
        pass