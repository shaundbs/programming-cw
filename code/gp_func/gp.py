from gp_state import StateGenerator, states
from loginsystem import database as db
import cli_ui as ui


class Gp:

    def __init__(self, user_id):
        # Create object from userId object from DB
        self.user_id = user_id

        # Get details
        self.db = db.Database()
        details_query = "SELECT FIRSTNAME, LASTNAME FROM USERS WHERE USERID = " + str(self.user_id)
        result = self.db.fetch_data(details_query)
        self.firstname, self.lastname = result[0][0].capitalize(), result[0][1].capitalize()

        # define states
        # self.states = [
        #     "main_options",  # homepage, initial options
        #     "confirm_appts",  # page to confirm appts
        #     "calendar_options"  # initial manage cal options
        # ]

        self.state_gen = StateGenerator(state_dict=states, state_object=self)

    def print_welcome(self):
        print("Hi Dr", self.firstname, self.lastname)

    def main_options(self):
        selected = ui.ask_choice("choose an option", choices=self.state_gen.get_state_options(), sort=False)
        print(selected + "------>")
        self.state_gen.get_func
