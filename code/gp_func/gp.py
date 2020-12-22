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


        # initialise state machine
        self.state_gen = StateGenerator(state_dict=states, state_object=self)
        self.state_gen.change_state("main options") # initialise main options state

    def print_welcome(self):
        print("Hi Dr", self.firstname, self.lastname)

    def main_options(self):
        self.print_welcome() # say hi to the Dr.

        selected = ui.ask_choice("choose an option", choices=self.state_gen.get_state_options(), sort=False)
        print(selected + "------>")
        self.state_gen.change_state(selected)

    # CALENDAR HANDLING

    def manage_calendar(self):
        print("hi this is the calendar")

        choice_list = self.state_gen.get_state_options()
        choice_list.append("Go back")

        selected = ui.ask_choice("Where to go next?", choices=choice_list, sort=False)
        if selected == "Go back":
            self.state_gen.call_prev_state()
        else:
            self.state_gen.change_state(selected)

    def view_calendar(self):
        pass

    def schedule_time_off(self):
        pass

    def confirm_appointments(self):
        pass

