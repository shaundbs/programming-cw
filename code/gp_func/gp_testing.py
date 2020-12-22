import sqlite3
from loginsystem import database as db
from gp_func.gp import Gp

if __name__ == '__main__':

    # get test user ID bypass login for testing purposes.
    user_id = db.Database().fetch_data("SELECT USERID FROM USERS WHERE EMAIL = 'qr@test.com'")

    user = Gp(user_id[0][0])

    user.print_welcome()

# print(user.state)




# user.to_confirm_appts()

print(user.state)

