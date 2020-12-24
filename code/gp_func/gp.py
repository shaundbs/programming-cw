from state_manager import StateGenerator
import gp_database as db
import cli_ui as ui
import gp_utilities as util
from time import sleep

# state dictionary/graph to map out possible routes/options from each state/node.
# back button should be child node if available option from a state.

states = {
    "main options": ["manage calendar", "confirm appointments", "view appointments"],
    # Calendar / holiday
    "manage calendar": ["view calendar", "schedule time off", "back"],
    "view calendar": ["back"],
    "schedule time off": ["back"],
    # confirm appts
    "confirm appointments": ["back"],
    # view appts
    "view appointments": ["show appointments from another day", "show appointment details", "back"],
    "show appointments from another day": ["back"],
    "show appointment details": ["write prescriptions", "back"]
}


class Gp:

    def __init__(self, user_id):
        # Create object from userId object from DB
        self.user_id = user_id

        # Get details
        self.db = db.Database()
        details_query = "SELECT FIRSTNAME, LASTNAME FROM USERS WHERE USERID = " + str(self.user_id)
        result = self.db.fetch_data(details_query)
        self.firstname, self.lastname = result[0]['firstName'].capitalize(), result[0]['lastName'].capitalize()

        # initialise state machine
        self.state_gen = StateGenerator(state_dict=states, state_object=self)
        # self.state_gen.change_state("main options")  # initialise main options state
        self.state_gen.change_state("confirm appointments")

    def print_welcome(self):
        ui.info_section(ui.blue, 'Welcome to the GP Dashboard')
        print("Hi Dr", self.firstname, self.lastname)

    # to handle whether we need to change state, or whether to call parent state if "back" is selected.
    def handle_state_selection(self, selected):
        if selected == 'back':
            self.state_gen.call_parent_state()
        else:
            self.state_gen.change_state(selected)

    # FUNCTIONS FOR EACH STATE

    def main_options(self):
        self.print_welcome()  # say hi to the Dr.

        selected = util.user_select("Choose an option", self.state_gen.get_state_options())

        self.handle_state_selection(selected)

    # CALENDAR HANDLING

    def manage_calendar(self):
        print("hi this is the calendar")

        selected = util.user_select("Where to go next?", self.state_gen.get_state_options())
        self.handle_state_selection(
            selected)  # if back is selected, the back state function above will handle going back to parent state.

    def view_calendar(self):
        pass

    def schedule_time_off(self):
        pass

    # CONFIRM APPOINTMENTS

    def confirm_appointments(self):
        ui.info_section(ui.blue, "Confirm Appointments")
        # show requested appt booking for GP
        query = f"SELECT APPOINTMENT_ID,  u.firstName || ' ' || u.lastName as 'patient name',  strftime('%d/%m/%Y', " \
                f"s.starttime) as date, strftime('%H:%M', s.starttime)  as 'appointment time' FROM APPOINTMENT  a " \
                f"left join Users u " \
                f" on u.userId = a.patient_id left join slots s on s.slot_id = a.slot_id WHERE IS_CONFIRMED= 0  AND " \
                f"IS_REJECTED= 0 AND GP_ID = {self.user_id}  order by s.starttime"
        res = self.db.fetch_data(query)
        ui.info(ui.standout, f"You have {len(res)} unconfirmed appointments.")

        # While there are unconfirmed appointments
        while res:
            table_data = util.output_sql_rows(res, ["date", "appointment time", "patient name"])
            print(table_data)
            user_choices = ["confirm all", "reject all", "confirm or reject an individual appointment", "back"]

            selected = ui.ask_choice("What would you like to do?", choices=user_choices)

            # CHOICES HANDLING
            if selected == user_choices[0]:  # accept all
                success = util.db_update(res, "appointment", "appointment_id", **{"is_confirmed": 1})
                if success:
                    ui.info(ui.green, "All appointments successfully confirmed.")
                else:
                    ui.info("There was an error, processing your request, please try later")

            elif selected == user_choices[1]:  # reject all
                success = util.db_update(res, "appointment", "appointment_id", **{"is_rejected": 1})
                if success:
                    ui.info(ui.green, "All appointments successfully rejected.")
                else:
                    ui.info("There was an error, processing your request, please try later")

            elif selected == user_choices[2]:  # action individually
                ui.info_1(selected)
                print(table_data)
                choice = ""
                valid_choices = [x for x in range(len(res))]
                while choice not in valid_choices:
                    try:
                        choice = ui.ask_string(
                            "Select an appointment to confirm or reject. Please enter an appointment's row number:")
                        choice = int(choice) - 1  # to match index
                        selected_row = res[choice]
                    except ValueError:
                        print("Please enter a number.")
                    except IndexError:
                        print("PLease enter a valid number found in the row column of the table.")

                # choose accept or reject or back
                further_options = ["confirm", "reject", "back"]
                selected = ui.ask_choice("What would you like to do with this appointment?", choices=further_options)
                if selected == further_options[2]:  # back
                    self.to_confirm_appointments()
                elif selected == further_options[0]:  # accept
                    success = util.db_update([selected_row], "appointment", "appointment_id", **{"is_confirmed": 1})
                    if success:
                        ui.info(ui.green,
                                f"Appointment on {selected_row['date']} with {selected_row['patient name']} successfully confirmed.")
                    else:
                        ui.info("There was an error, processing your request, please try later")
                elif selected == further_options[1]:  # reject
                    success = util.db_update([selected_row], "appointment", "appointment_id", **{"is_rejected": 1})
                    if success:
                        ui.info(ui.green,
                                f"Appointment on {selected_row['date']} with {selected_row['patient name']} successfully rejected.")
                    else:
                        ui.info("There was an error, processing your request, please try later")

            else:
                self.handle_state_selection(selected)  # back
            res = self.db.fetch_data(query)  # refresh result.

        else:  # no unconfirmed appointments
            ui.info_2("Not much else to do here without any unconfirmed appointments")
            yes = ui.ask_yes_no("Go back to the homepage?")
            if yes:
                self.handle_state_selection("back")
            else:
                ui.info("Well, nothing to do here. I'll take you back anyway")
                for i in range(2):
                    ui.dot()
                    sleep(0.8)
                ui.dot(last=True)
                self.handle_state_selection("back")  # back to main options
