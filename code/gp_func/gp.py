from transitions import Machine
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
        self.states = [
            "main_options",  # homepage, initial options
            "confirm_appts",  # page to confirm appts
            "calendar_options"  # initial manage cal options
        ]

        self.flow = Machine(model=self, states=self.states, initial="main_options")

    def print_welcome(self):
        print("Hi Dr", self.firstname, self.lastname)

    def main_options(self):
        selected = ui.ask_choice("choose an option", choices=self.states, sort=False)
        print(selected)
