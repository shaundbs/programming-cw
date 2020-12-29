import os
import sys

# sys.path.append(os.path.dirname(
#     "/"))

import gp_database as db
from gp import Gp

if __name__ == '__main__':
    # get test user ID bypass login for testing purposes.
    user_id = db.Database().fetch_data("SELECT USERID FROM USERS WHERE EMAIL = 'qr@test.com'")

    # print(user_id)

    user = Gp(user_id[0]['userId'])
    print("LOGGED OUT!!!! out of code now.")


    # user.state_gen.call_prev_state()

    # user.print_welcome()

# print(user.state)


# user.to_confirm_appts()

# print(user.state)
