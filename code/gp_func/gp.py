from state_manager import StateGenerator
import gp_database as db
import cli_ui as ui
import gp_utilities as util
from datetime import datetime

# state dictionary/graph to map out possible routes/options from each state/node.
# back button should be child node if available option from a state.

states = {
    "main options": ["manage calendar", "confirm appointments", "view my appointments", "logout"],
    # Calendar / holiday
    "manage calendar": ["view calendar", "schedule time off", "back"],
    "view calendar": ["back"],
    "schedule time off": ["back"],
    # confirm appts
    "confirm appointments": ["back"],
    # view appts
    "view my appointments": ["select an appointment", "view appointments from another day", "back"],
    "select an appointment": ["show appointment details", "back"],
    "view appointments from another day": ["back"],
    "show appointment details": ["write prescriptions", "add referral", "back"],
    "write prescriptions": ["back"],
    "add referral": ["back"]
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
        self.state_gen.change_state("main options")  # initialise main options state

        # Initialise state variables (variables that need to be passed between states and hold a value until they are
        # reset in the application flow).
        self.curr_appt_date = "today"  # default is today
        self.curr_appt_id = None  # no appoinment id set yet.

    def print_welcome(self):
        ui.info_section(ui.blue, 'Welcome to the GP Dashboard')
        print("Hi Dr", self.firstname, self.lastname)

    def logout(self):
        # TODO return to main code. delete class instance.
        pass

    # to handle whether we need to change state, or whether to call parent state if "back" is selected.
    def handle_state_selection(self, selected):
        if selected == 'back':
            self.state_gen.call_parent_state()
        else:
            self.state_gen.change_state(selected)

    # FUNCTIONS FOR EACH STATE

    def main_options(self):
        self.print_welcome()  # say hi to the Dr.
        # reset state variable if back to main options.
        self.curr_appt_date = "today"

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
                selected_row = util.select_table_row(res, table_data,
                                                     "Select an appointment to confirm or reject. Please enter an appointment's row number:")

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
                util.loading()
                self.handle_state_selection("back")  # back to main options

    # View today's or another day's appointments and initiate consultations.
    def view_my_appointments(self):
        # TODO - add details on how to use. I.e. show appt details to begin a consultation.

        # state variables
        self.curr_appt_id = None  # reset current appointment if previously declared
        appt_date = self.curr_appt_date

        ui.info_section(ui.blue, "View your appointments")
        ui.info(f"showing appointments for {str(appt_date)}")
        if appt_date == "today":
            date = "date('now')"
        else:

            date = f"'{appt_date}'"
        # get appointments for the GP user
        get_appts_sql_query = "SELECT appointment_id,  u.firstName || ' ' || u.lastName as 'patient name',  strftime(" \
                              f"'%d/%m/%Y', " \
                              f"s.starttime) as date, strftime('%H:%M', s.starttime)  as 'appointment time' FROM APPOINTMENT  a " \
                              f"left join Users u " \
                              f" on u.userId = a.patient_id left join slots s on s.slot_id = a.slot_id WHERE IS_CONFIRMED= 1 and  " \
                              f"GP_ID = {self.user_id}  and date(s.starttime) = {date} order by s.starttime "

        res = self.db.fetch_data(get_appts_sql_query)
        ui.info_2(ui.standout, f"{appt_date} - you have {len(res)} appointment(s)")
        # show appts table
        if res:
            table_data = util.output_sql_rows(res, ["date", "appointment time", "patient name"])
            print(table_data)
            selected = util.user_select("What would you like to do?", choices=self.state_gen.get_state_options())
            if selected == "select an appointment":
                self.to_select_an_appointment(res, table_data)  # handle state transition manually as state
                # requires 2 arguments.
            else:
                self.handle_state_selection(selected)

        else:
            selected = util.user_select("What would you like to do?", choices=self.state_gen.get_state_options()[1:])
            self.handle_state_selection(selected)

    def select_an_appointment(self, appointment_list, appt_table):
        """

                :param appointment_list: sql result of appts nested dictionaries in a list
                :param appt_table: table to be given to print function
                :return:
                """
        # assert that function arguments have been given. if not go back to view_my_appointments

        # if only one appointment given from table, no need to ask user. Enter appt options.
        if len(appointment_list) == 1:
            selected_row = appointment_list[0]
        # If more than one, need to ask user to select from table by row id.
        else:
            selected_row = util.select_table_row(appointment_list, appt_table,
                                                 "Select an appointment by entering its row number:")

        try:
            appt_id = selected_row["appointment_id"]

            # Set state current appointment variable for dependant states
            self.curr_appt_id = appt_id

            if len(appointment_list) == 1:
                ui.info_1("Only one appointment found. Appointment auto-selected.\nNavigating to appointment "
                          "information.")
                util.loading()
            self.to_show_appointment_details()
        except KeyError:
            # TODO LOG ERROR IF INVALID DICTIONARY PASSED TO FUNCTION.
            ui.info(ui.red, "An error has occured. We could not get the appointment data for the record.")
            ui.info("Going back to 'view appointment' page")
            util.loading()
            self.handle_state_selection("back")

    def show_appointment_details(self):

        appt_id = self.curr_appt_id  # grab state variable of current appointment

        # show more details - name, appt reason etc.
        # Appt details + referral
        get_apt_details_query = f"SELECT appointment_id,  u.firstName || ' ' || u.lastName as 'patient name',  " \
                                f"strftime('%d/%m/%Y', s.starttime) as date, strftime('%H:%M', s.starttime)  as " \
                                f"'appointment time', reason, referred_specialist_id FROM APPOINTMENT  a left join Users u on u.userId = " \
                                f"a.patient_id left join slots s on s.slot_id = a.slot_id WHERE appointment_id= " \
                                f"{appt_id} "
        appt_details = self.db.fetch_data(get_apt_details_query)
        # todo: add check that there is only one record returned. if not == problem

        # Prescription
        prescription_query = f"select * from Prescription where appointment_id = {appt_id}"
        prescription_data = self.db.fetch_data(prescription_query)

        # Base details
        if appt_details[0]['reason'] is None:
            reason = "Not specified"
        else:
            reason = appt_details[0]['reason']

        ui.info_section(ui.bold, "Appointment Information")
        ui.info(ui.bold, "Appointment date:", ui.reset, f"{appt_details[0]['date']}")
        ui.info(ui.bold, "Appointment time:", ui.reset, f"{appt_details[0]['appointment time']}")
        ui.info(ui.bold, "Patient Name:", ui.reset, f"{appt_details[0]['patient name']}")
        ui.info(ui.bold, "Reason for appointment:", ui.reset, f"{reason} \n")

        # Clinical notes

        # Prescriptions
        if len(prescription_data) == 0:
            ui.info(ui.bold, "Prescriptions:", ui.reset, "None prescribed yet.\n")
        else:
            columns = ["medicine_name", "treatment_description", "pres_frequency_in_days", "startDate", "expiryDate"]
            headers = ["Medicine", "Treatment", "Repeat prescription (days)", "Start date", "Prescription valid until"]
            pres_table = util.output_sql_rows(prescription_data, columns, headers, table_title="Prescriptions")
            print(pres_table)

        # Referrals
        if appt_details[0]["referred_specialist_id"] is None:
            ui.info(ui.bold, "Referral:", ui.reset, "No referral added.\n")
        else:
            # Need to grab info from db for referral.
            referral_query = f"SELECT 'Dr '||firstName||' '||lastName as doc_name, hospital, specialist_id, d.name as " \
                             f"dept_name from Specialists left join Department d using(department_id) where " \
                             f"specialist_id = {appt_details[0]['referred_specialist_id']} "
            referral = self.db.fetch_data(referral_query)
            ui.info(ui.bold, "Referral:", ui.reset,
                    f"{referral[0]['dept_name']} department - {referral[0]['doc_name']} at {referral[0]['hospital']}.\n")

        # offer options for this state (write/edit notes, prescriptions, referals, finalise appt, view patient records.)
        selected = util.user_select("How would you like to proceed?", self.state_gen.get_state_options())
        if selected == "write prescriptions":
            self.to_write_prescriptions(appt_id)  # handle manually as state requires appt_id argument
        elif selected == "back":  # need to skip select appointment
            self.to_view_my_appointments()
        else:
            self.handle_state_selection(selected)

    def write_prescriptions(self, appt_id):
        ui.info("Please follow the prompts to enter a prescription for the patient.")

        prescription_insert_stmt = "INSERT INTO PRESCRIPTION (medicine_name, treatment_description, " \
                                   "pres_frequency_in_days, startDate, expiryDate, appointment_id) VALUES (?,?,?,?,?," \
                                   "?) "

        medicine = ui.ask_string(ui.blue, "Please enter the name of the prescribed medicine:")
        treatment = ui.ask_string(ui.blue, "Please enter the treatment being prescribed\n(e.g. One tablet twice a "
                                           "day for three weeks):")
        if ui.ask_yes_no(ui.blue, "Will this be a repeat prescription?"):
            freq_chosen = False
            while not freq_chosen:
                pres_frequency = ui.ask_string("For this repeat prescription, please enter the frequency (in days) "
                                               "between prescriptions:")
                try:
                    int(pres_frequency)
                    freq_chosen = True
                except ValueError:
                    ui.info("Please enter a number.")
        else:
            pres_frequency = 0

        start_chosen = False
        while not start_chosen:
            ui.info("When will this prescription be valid from? \n(If valid from today, then you can enter 'today', "
                    "otherwise enter a date in the future.)")
            start_date = util.get_user_date()
            # check date is in the future
            if datetime.strptime(start_date, '%Y-%m-%d') >= datetime.today().replace(hour=0, minute=0, second=0,
                                                                                     microsecond=0):
                start_chosen = True
            else:
                ui.info(ui.red, "Invalid date. Please choose a date either today or in the future.")

        expiry_chosen = False
        while not expiry_chosen:
            ui.info("When should this prescription expire?")
            expiry_date = util.get_user_date()
            # check date after or equal to start date
            if datetime.strptime(expiry_date, '%Y-%m-%d') >= datetime.strptime(start_date, '%Y-%m-%d'):
                expiry_chosen = True
            else:
                ui.info(ui.red,
                        f"Invalid date. Please choose a date on or after the entered start date ({start_date}) of this prescription.")

        # present prescription details + offer to save.
        ui.info("\nForm completed. The prescription entry is:\n")
        ui.info(ui.bold, "Prescribed Medicine:", ui.reset, f"{medicine}")
        ui.info(ui.bold, "Treatment:", ui.reset, f"{treatment}")
        ui.info(ui.bold, "Prescription frequency (days):", ui.reset, f"{pres_frequency}")
        ui.info(ui.bold, "Start date:", ui.reset, f"{start_date}")
        ui.info(ui.bold, "Expiry date:", ui.reset, f"{expiry_date}\n")

        if ui.ask_yes_no("Are these details correct? Would you like to save this prescription?"):
            err = self.db.exec_one(prescription_insert_stmt,
                                   (medicine, treatment, pres_frequency, start_date, expiry_date, appt_id))
            if err is None:
                ui.info_1("Prescription successfully saved in records.")
            else:
                # TODO  log error
                ui.error("Sorry, an error occurred when saving. Please try again later.")

        user_options = ["write another prescription", "back"]
        selected = util.user_select("How would you like to proceed?", choices=user_options)
        if selected == "write another prescription":
            self.to_write_prescriptions(appt_id)
        elif selected == "back":
            self.to_show_appointment_details()

    def add_referral(self):
        appt_id = self.curr_appt_id  # get current state appointment id

        ui.info_section("Refer this patient to a specialist")

        # if referral already populated. This will be overwritten, by continuing. Proceed? or back?
        referral_check_query = f"SELECT referred_specialist_id, 'Dr '||s.firstName||' '||s.lastName as doc_name, " \
                               f"s.hospital, d.name as dept_name FROM APPOINTMENT a left join Specialists " \
                               f"s on s.specialist_id = " \
                               f"a.referred_specialist_id left join Department d on d.department_id = s.department_id " \
                               f"WHERE appointment_id= " \
                               f"{appt_id} "  # TODO add another left join to get dept
        referral_check = self.db.fetch_data(referral_check_query)
        if referral_check is not None:
            # Show current referral details
            ui.info(f"A patient can only be referred once per appointment.\nA referral has already been added for "
                    f"this appointment: {referral_check[0]['dept_name']} department - {referral_check[0]['doc_name']} at {referral_check[0]['hospital']} ")
            proceed = ui.ask_yes_no("Would you like to proceed? If yes, the current referral will be "
                                    "updated/overwritten.")
            if not proceed:
                ui.info("Returning to appointment details")
                util.loading()
                # Return to Appointment details
                self.to_show_appointment_details()

            # select referral category
        # get referral categories
        referral_cats_query = "SELECT * FROM DEPARTMENT"
        referral_cats = self.db.fetch_data(referral_cats_query)
        referral_cat_table = util.output_sql_rows(referral_cats, ["name"], ["department name"], "Referral departments")
        selected_category = util.select_table_row(referral_cats, referral_cat_table, "Please select a referral "
                                                                                     "department category, "
                                                                                     "by entering its row number:")
        dept_id = selected_category["department_id"]
        dept_name = selected_category["name"]

        # for chosen department id, present GP with possible doctors to choose.
        ui.info_1(f"{dept_name} selected.")
        ui.info_2(f"Currently viewing available doctors for the {dept_name} department in the UK.")

        referral_docs_query = f"SELECT 'Dr '||firstName||' '||lastName as doc_name, hospital, specialist_id from " \
                              f"Specialists where department_id = {dept_id}"
        referral_docs = self.db.fetch_data(referral_docs_query)
        referral_table = util.output_sql_rows(referral_docs, ["doc_name", "hospital", ], ["Doctor", "Hospital"])

        selected_doc = util.select_table_row(referral_docs, referral_table, "Please select a doctor for referral "
                                                                            "based on the patients preferred "
                                                                            "hospital location.")
        selected_doc_id = selected_doc["specialist_id"]
        if ui.ask_yes_no(f"Please confirm this referral to {selected_doc['doc_name']} at {selected_doc['hospital']}"):
            # if True i.e. confirmed choice
            # update appointment table for this appt_id
            success = util.db_update([{"appointment_id": appt_id}], "Appointment", "appointment_id",
                                     **{"referred_specialist_id": selected_doc_id})
            if success:

                ui.info(ui.green, "Referral successfully added.")
            else:
                ui.info("There was an error, processing your request, please try later")
        ui.info("Returning to appointment details")
        util.loading()
        # Return to Appointment details
        self.to_show_appointment_details()

    def view_appointments_from_another_day(self):
        ui.info(ui.blue, "View appointments from another day.")
        date_not_chosen = True
        while date_not_chosen:

            date_to_search = util.get_user_date()
            # date validation. Can be any date if in valid format. If too far in past or in future, no appts will be
            # shown via self.view_my_appointments

            if ui.ask_yes_no(f"Search for appointments on {date_to_search}?"):
                date_not_chosen = False

        ui.info(f"Fetching your appointments for {date_to_search}")
        util.loading()
        self.curr_appt_date = date_to_search
        self.to_view_my_appointments()
