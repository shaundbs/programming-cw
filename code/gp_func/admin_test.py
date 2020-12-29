from state_manager import StateGenerator
import gp_database as db
from admin import Admin

if __name__ == '__main__':
    # get test user ID bypass login for testing purposes.
    user_id = db.Database().fetch_data("SELECT USERID FROM USERS WHERE EMAIL = 'ez@test.com'")

    user = Admin(user_id[0]['userId'])

