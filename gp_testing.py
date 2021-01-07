from gp_func import gp_database as db
from gp_func.gp import Gp
import logging

if __name__ == '__main__':
    logging.basicConfig(filename='gp.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

    # get test user ID bypass login for testing purposes.
    # user_id = db.Database().fetch_data("SELECT USERID FROM USERS WHERE EMAIL = 'qr@test.com'")

    # print(user_id)

    user = Gp(15)
    print("LOGGED OUT!!!! out of code now.")


    # user.state_gen.call_prev_state()

    # user.print_welcome()

# print(user.state)


# user.to_confirm_appts()

# print(user.state)
