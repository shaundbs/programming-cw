from state_manager import StateGenerator
import loginsystem
import cli_ui as ui
import gp_utilities as util

# state dictionary/graph to map out possible routes from each state/node.
# back button should be child node if available option from a state.

states = {
    "main options": ["manage calendar", "confirm appointments", "view appointments"],
    # Calendar / holiday
    "manage calendar": ["view calendar", "schedule time off", "back"],
    "view calendar": [],
    "schedule time off": [],
    # confirm appts
    "confirm appointments": [],
    # view appts
    "view appointments": ["show appointments from another day", "show appointment details", "back"],
    "show appointments from another day": [],
    "show appointment details": ["write prescriptions"]
}


class Gp:

    def __init__(self, user_id):
        # Create object from userId object from DB
        self.user_id = user_id

        # Get details
        self.db = loginsystem.database.Database()
        details_query = "SELECT FIRSTNAME, LASTNAME FROM USERS WHERE USERID = " + str(self.user_id)
        result = self.db.fetch_data(details_query)
        self.firstname, self.lastname = result[0][0].capitalize(), result[0][1].capitalize()

        # initialise state machine
        self.state_gen = StateGenerator(state_dict=states, state_object=self)
        self.state_gen.change_state("main options")  # initialise main options state

    def print_welcome(self):
        print("Hi Dr", self.firstname, self.lastname)

    def handle_state_selection(self, selected):
        if selected == 'back':
            self.state_gen.call_parent_state()
        else:
            self.state_gen.change_state(selected)

    # FUNCTIONS FOR EACH STATE

    def main_options(self):
        self.print_welcome()  # say hi to the Dr.

        selected = util.user_select("Choose and option", self.state_gen.get_state_options())

        print(selected + "------>")
        self.handle_state_selection(selected)

    # CALENDAR HANDLING

    def manage_calendar(self):
        print("hi this is the calendar")

        selected = util.user_select("Where to go next?", self.state_gen.get_state_options())
        self.handle_state_selection(selected) # if back is selected, the back state function above will handle going back to parent state.

    def view_calendar(self):
        pass

    def schedule_time_off(self):
        pass

    # CONFIRM APPOINTMENTS

    def confirm_appointments(self):
        pass
        # show requested appt booking for GP
        query = f"SELECT SLOT_ID, APPOINTMENT_ID, PATIENT_ID FROM APPOINTMENT WHERE IS_CONFIRMED = 0 AND IS_REJECTED = 0 AND GP_ID = {self.user_id}"
        res = self.db.fetch_data(query)
        print(res)

        # accept all
        # reject all
        # accept/reject individual appt
