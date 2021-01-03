import sqlite3
import bcrypt
import getpass  # hide password when inputting
from database import Database
from sqlite3 import Error
from pandas import DataFrame
from tabulate import tabulate
from os import system
import getpass

def main(): 
    # give admin user homepage options 
    admins_option = adminOptions() 
    # admin user wants to manage GP accounts 
    if admins_option == '2':
        #  view table of GP users 
        gp_df = viewGP()
        #  retrieve id of GP account admin wants to manage 
        chosen_gp_id = showGP(gp_df)
        #  admin user chooses what they want to do with GP account
        manage_gp_option = manageGPOptions()
        # admin user wants to edit GP account information
        if manage_gp_option == "1":
            updateGP(chosen_gp_id)
            main()
        # admin user wants to delete GP acccount
        if manage_gp_option == "2":
            deleteGP(chosen_gp_id)
            main()
        # admin user wants to deactivate GP account 
        if manage_gp_option == "3":
            deactivateGP(chosen_gp_id)
            main()
        # admin user wants to reactivate GP account 
        if manage_gp_option == "4":
            reactivateGP(chosen_gp_id)
            main()
    #  admin user wants to log out of program 
    elif admins_option == '9':
        print('logout option chosen')

def clear():
        _ = system('clear')

def adminOptions(): 
    clear()
    print('\n' + '1. Manage Patients')
    print('2. Manage GP')
    print('3. Register new GP')
    print('4. Approve new Patient')
    print('9. Log Out')
    admin_option = input('Please choose an option: ')
    return admin_option


def viewGP():
    # form database connection 
    conn = None
    try: 
        conn = sqlite3.connect('database/ehealth.db')
    except Error as e:
        print(e)
    cur = conn.cursor()
    # execute query 
    gp_account = ['gp', ]
    cur.execute('SELECT userID, firstName, lastName, email FROM users WHERE accountType = ?', gp_account)
    rows = cur.fetchall()
    # generate printout
    gp_dataframe_header = ['ID', 'First Name', 'Last Name', 'email']
    gp_dataframe = DataFrame(rows)
    gp_dataframe.columns = gp_dataframe_header
    clear()
    return gp_dataframe


def showGP(GpDataFrame):
    # display gp table
    gp_table = tabulate(GpDataFrame, headers='keys', tablefmt='fancy_grid', showindex=False)
    print('\n' + gp_table)
    # allow admin user to choose desired gp account
    chosen_gp_id = int(input('Please enter the ID of the GP whose record you wish to view from the table above: '))
    gp_id_list = GpDataFrame['ID'].tolist()
    print(gp_id_list)
    if (chosen_gp_id in gp_id_list): 
        return chosen_gp_id


def manageGPOptions():
    clear()
    print('\n' + '1. Edit GP account information')
    print('2. Remove GP account')
    print('3. Deactivate GP account')
    print('4. Deactivate GP account')
    manage_gp_option = input('Please choose an option: ')
    return manage_gp_option

def deactivateGP(chosen_gp_id):
    clear()
    deactivate_confirm = input('Are you sure you want to deactive this GP account (y/n)?')
    if deactivate_confirm.lower() == "y":
        # form database connection 
        conn = None
        try: 
            conn = sqlite3.connect('database/ehealth.db')
        except Error as e:
            print(e)
        cur = conn.cursor()
        cur.execute('''UPDATE Users SET is_active=0 WHERE userID=?''', [chosen_gp_id])
        conn.commit() 
    return 0

def reactivateGP(chosen_gp_id):
    clear()
    reactivate_confirm = input('Are you sure you want to reactivate this GP account (y/n)?')
    if reactivate_confirm.lower() == "y":
        # form database connection 
        conn = None
        try: 
            conn = sqlite3.connect('database/ehealth.db')
        except Error as e:
            print(e)
        cur = conn.cursor()
        cur.execute('''UPDATE Users SET is_active=1 WHERE userID=?''', [chosen_gp_id])
        conn.commit() 
    return 0

def deleteGP(chosen_gp_id):
    clear()
    delete_gp_confirm = input('Are you sure you want to premanently delete this GP account.(y/n)?')
    if delete_gp_confirm.lower() == "y":
        # form database connection 
        conn = None
        try: 
            conn = sqlite3.connect('database/ehealth.db')
        except Error as e:
            print(e)
        cur = conn.cursor()
        cur.execute("DELETE FROM Users WHERE userID=?",[chosen_gp_id])
        conn.commit() 
    return 0

def updateGP(chosen_gp_id):
    # get admin user request
    clear()
    update_option = updateGPOptions()
    db = Database()
    # if admin user wants to change first name
    if update_option == 1:
        new_fName = input("Enter the new First Name: ")
        new_lName = input("Enter the new Last Name: ")
        db.exec_one("""UPDATE Users SET FirstName=?,LastName=? WHERE userID=?""", [new_fName,new_lName,chosen_gp_id])
        clear()
        updateGP(chosen_gp_id)
    # if admin user wants to change email 
    if update_option == 2:
        new_email = input("Enter the GP's new email address: ")
        db.exec_one("""UPDATE Users SET email=?  WHERE userID=?""", [new_email, chosen_gp_id])
        clear()
        updateGP(chosen_gp_id)
    # if admin user wants to reset GP user's password 
    if update_option == 3:
        pWord = getpass.getpass('Password:')
        pWord = pWord.encode('utf-8')
        # hash password
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(pWord, salt)
        # update password in db
        db.exec_one("""UPDATE Users SET password=?  WHERE userID=?""", [hashed_pw, chosen_gp_id])
        clear()
        updateGP(chosen_gp_id)
    
    if update_option == 4:
        return update_option


def updateGPOptions():
    clear()
    print('\n' + '1. Change GP\'s name')
    print('2. Change GP\'s registered email address')
    print('3. Reset GP\'s password')
    print('4. go back to admin menu')
    update_gp_options = int(input('Please choose an option: '))
    return update_gp_options


# only run if this module being run (As test module only )
if __name__ == "__main__":
    main()
