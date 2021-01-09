import calendar
import csv
import logging
from datetime import datetime, timedelta
import os
from sqlite3 import OperationalError
import sys

import cli_ui as ui

from . import gp_database as db
from . import gp_utilities as util
from state_manager import StateGenerator

# state dictionary/graph to map out possible routes/options from each state/node.
# back button should be child node if available option from a state.

states = {
    "Main options": ["Manage calendar", "Confirm appointments", "View my appointments", "Logout"],
    "Logout": [],
    # Calendar / holiday
    "Manage calendar": ["View calendar", "Schedule time off", "Back"],
    "View calendar": ["View another month", "View day schedule", "Back"],
    "View day schedule": ["Back"],
    "Schedule time off": ["Back"],
    # confirm appts
    "Confirm appointments": ["Back"],
    # view appts
    "View my appointments": ["Select an appointment", "View appointments from another day", "Back"],
    "Select an appointment": ["Show appointment details", "Back"],
    "View appointments from another day": ["Back"],
    "Show appointment details": ["Write clinical notes", "Write prescriptions", "Add referral", "Finalise appointment",
                                 "View patient medical history", "Back"],
    "Write clinical notes": ["Back"],
    "Write prescriptions": ["Back"],
    "Add referral": ["Back"],
    "Finalise appointment": ["Back"],
    "View patient medical history": ["View previous appointment records", "Back"],
    "View previous appointment records": ["View patient records by recency", "Download all records as a csv", "Back"],
    "View patient records by recency": ["Back"],
    "Download all records as a csv": ["Back"]

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
        self.curr_appt_id = None  # no appointment id set yet.
        self.curr_appt_month = "current_month"
        self.patient_id = None
        self.prev_appt_records = None

    def print_welcome(self):
        ui.info_section(ui.blue, 'Welcome to the GP Dashboard')
        print("Hi Dr", self.firstname, self.lastname)

    def logout(self):
        # remove state tracking from the object. exiting out of app.
        del self.state_gen
        ui.info("Logging out and exiting application.")
        sys.exit()

    # to handle whether we need to change state, or whether to call parent state if "back" is selected.
    def handle_state_selection(self, selected):
        if selected.lower() == 'back':
            self.state_gen.call_parent_state()
        else:
            self.state_gen.change_state(selected)

    # FUNCTIONS FOR EACH STATE

    def main_options(self):
        util.sys_clear()
        self.print_welcome()  # say hi to the Dr.
        # reset state variable if back to main options.
        self.curr_appt_date = "today"
        self.curr_appt_month = "current_month"

        # instructions
        ui.info(ui.faint, "\nInfo:"
                          "\n'Manage calendar' to book time off, see your scheduled appointments and booked holiday. "
                          "\n'Confirm appointments' to confirm or reject appointments patients have "
                          "requested with you. "
                          "\n'View my appointments' to view your appointments for today or another day and begin your "
                          "consultations.\n")

        selected = util.user_select("Choose an option", self.state_gen.get_state_options())

        self.handle_state_selection(selected)

    # CALENDAR HANDLING

    def manage_calendar(self):
        util.sys_clear()
        print("Welcome to your calendar")
        self.curr_appt_month = "current_month"

        selected = util.user_select("Where to go next?", self.state_gen.get_state_options())
        self.handle_state_selection(
            selected)  # if back is selected, the back state function above will handle going back to parent state.

    def view_calendar(self):
        util.sys_clear()
        selected_month = datetime.now()
        if self.curr_appt_month == "current_month":
            month = datetime.today().strftime('%Y/%m')
        else:
            month = self.curr_appt_month

        # print(month, type(month))

        # get appointments for the GP user
        query = f"SELECT strftime('%Y/%m', s.starttime) as month, strftime('%d', s.starttime) as day FROM Appointment a " \
                f"LEFT JOIN slots s on a.slot_id=s.slot_id " \
                f"WHERE is_confirmed=1 AND GP_ID = {self.user_id} and month='{month}'"
        res = self.db.fetch_data(query)
        # create calendar
        c = calendar.TextCalendar()
        display_month = c.formatmonth(int(month[:4]), int(month[5:]))
        for appt in res:
            if appt["day"][0] == "0":
                display_month = display_month.replace(" %s " % appt["day"][1], "[%s]" % appt["day"][1])
            else:
                display_month = display_month.replace(" %s " % appt["day"], "[%s]" % appt["day"])

        ui.info(display_month)
        ui.info("Days that you have appointments are highlighted in brackets []")

        # user_choices = ["view day", "view another month", "back"]
        selected = ui.ask_choice("What would you like to do next?",
                                 choices=self.state_gen.get_state_options())
        if selected == "View day schedule":
            self.curr_appt_date = util.get_user_date()
            while datetime.strptime(self.curr_appt_date, '%Y-%m-%d').weekday() > 4:
                ui.info("There are no appointments at weekends, please select a weekday")
                self.curr_appt_date = util.get_user_date()

        elif selected == "View another month":
            self.curr_appt_month = util.get_user_month()
            self.to_view_calendar()

        self.handle_state_selection(selected)

    def view_day_schedule(self):
        date = self.curr_appt_date
        get_appts_sql_query = f"SELECT is_confirmed, strftime('%d/%m/%Y',s.starttime) as date, " \
                              f"strftime('%Y-%m-%d %H:%M:%S', s.starttime)  as 'appointment time' FROM slots s left " \
                              f"outer " \
                              f"join Appointment a on s.slot_id = a.slot_id " \
                              f"WHERE gp_id = {self.user_id} and date(s.starttime) = '{date}' order by s.starttime"

        get_slots_sql_query = f"SELECT startTime, endTime FROM slots " \
                              f"WHERE date(starttime) = '{date}' order by starttime"

        get_time_off_sql_query = f"SELECT startTime, endTime FROM gp_time_off " \
                                 f"WHERE date(starttime) <= '{date}'  AND date(endTime) >= '{date}'  " \
                                 f"order by startTime"

        slots = self.db.fetch_data(get_slots_sql_query)
        time_off = self.db.fetch_data(get_time_off_sql_query)
        appointments = self.db.fetch_data(get_appts_sql_query)

        for slot in slots:
            slot_start = datetime.strptime(slot["startTime"], '%Y-%m-%d %H:%M:%S')
            slot_end = datetime.strptime(slot["endTime"], '%Y-%m-%d %H:%M:%S')
            for time in time_off:
                time_off_start = datetime.strptime(time["startTime"], '%Y-%m-%d %H:%M:%S')
                time_off_end = datetime.strptime(time["endTime"], '%Y-%m-%d %H:%M:%S')
                if (time_off_start < slot_end) and (time_off_end > slot_start):
                    slot["status"] = "Time off"
            if "status" not in slot:
                slot["status"] = "Free slot"

        for slot in slots:
            for appointment in appointments:
                if slot["startTime"] == appointment["appointment time"]:
                    if appointment["is_confirmed"] == 1:
                        slot["status"] = "Confirmed appointment"
                    else:
                        slot["status"] = "Unconfirmed appointment"
        table_data = util.output_sql_rows(slots, ["startTime", "status"])
        print(table_data)
        selected = util.user_select("Where to now?", self.state_gen.get_state_options())

        self.handle_state_selection(selected)
        # options = ["Take specific slot off", "back"]
        # selected = ui.ask_choice("Would you like to?", choices=options)

    def schedule_time_off(self):
        util.sys_clear()
        now = datetime.now()
        # now = datetime.strptime("2020-01-01", '%Y-%m-%d')

        ui.info("When you would you like your time-off to start?")
        date_not_valid = True
        while date_not_valid:
            start_time = util.get_user_date()
            if datetime.strptime(start_time, '%Y-%m-%d') > now + timedelta(days=30):
                date_not_valid = False
            elif datetime.strptime(start_time, '%Y-%m-%d') > now:
                ui.info("Time-off must be booked more than 30 days in advance")
            else:
                ui.info("Time-off cannot be booked in the past")

        ui.info("When you would you like your time off to end?")
        date_not_valid = True
        while date_not_valid:
            end_time = util.get_user_date()
            if datetime.strptime(end_time, '%Y-%m-%d') >= datetime.strptime(start_time, '%Y-%m-%d'):
                date_not_valid = False
            else:
                ui.info("Cannot end before it begins")

        # check for appointments in that time period

        clash_query = f"SELECT s.starttime, a.is_confirmed, a.appointment_id " \
                      f"FROM slots s left join Appointment a on s.slot_id = a.slot_id " \
                      f"WHERE gp_id = {self.user_id} and IS_REJECTED= 0 and s.startTime BETWEEN '{start_time}' AND  '{end_time}' " \
                      f"order by s.starttime"

        appointments = self.db.fetch_data(clash_query)
        start_stamp = datetime.strptime(start_time, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
        end_stamp = (datetime.strptime(end_time, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        print(end_stamp)

        time_off_query = f"INSERT INTO gp_time_off (gp_id, startTime, endTime)" \
                         f"VALUES ({self.user_id}, '{start_stamp}', '{end_stamp}')"

        if not appointments:

            yes = ui.ask_yes_no(f"These dates are available. Are you sure you would like to book time off"
                                f" between the following dates?:\n {start_time} - {end_time}")
            if yes:
                self.db.exec(time_off_query)
                print("Time-off successfully booked")
            else:
                print("Booking cancelled")

            # TODO ERROR HANDLING

        elif appointments:
            print("You have the following clashing appointments:")
            table_data = util.output_sql_rows(appointments, ["startTime", "is_confirmed"])
            print(table_data)

            if not any(i['is_confirmed'] == 1 for i in appointments):
                yes = ui.ask_yes_no("Reject the following appointments?")
                if yes:
                    success = util.db_update(appointments, "appointment", "appointment_id", **{"is_rejected": 1})
                    if success:
                        ui.info(ui.green, "All appointments successfully rejected and time off booked")
                        self.db.exec(time_off_query)
                    else:
                        ui.info("There was an error, processing your request, please try later")


            else:
                print("Sorry, you have holiday dates unavailable")

        selected = ui.ask_choice("Where to?", choices=self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    # CONFIRM APPOINTMENTS

    def confirm_appointments(self):
        util.sys_clear()
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
            user_choices = ["Confirm all", "Reject all", "Confirm or reject an individual appointment", "Back"]

            selected = ui.ask_choice("What would you like to do?", choices=user_choices, sort=False)

            # CHOICES HANDLING
            if selected == "Confirm all":  # confirm all
                success = util.db_update(res, "appointment", "appointment_id", **{"is_confirmed": 1})
                if success:
                    ui.info(ui.green, "All appointments successfully confirmed. Sending status update emails to "
                                      "patients in background.")
                    # threading - send emails for every record in result
                    for record in res:
                        util.create_thread_task(util.send_appt_confirmation_email,
                                                function_arguments_tuple=(record['appointment_id'], True))

                else:
                    ui.info("There was an error, processing your request, please try later")

            elif selected == "Reject all":  # reject all
                success = util.db_update(res, "appointment", "appointment_id", **{"is_rejected": 1})
                if success:
                    ui.info(ui.green, "All appointments successfully rejected. Sending status update emails to "
                                      "patients in background.")
                    # threading - send emails for every record in result.
                    for record in res:
                        util.create_thread_task(util.send_appt_confirmation_email,
                                                function_arguments_tuple=(record['appointment_id'], False))
                else:
                    ui.info("There was an error, processing your request, please try later")

            elif selected == "Confirm or reject an individual appointment":  # action individually
                ui.info_1(selected)
                selected_row = util.select_table_row(res, table_data,
                                                     "Select an appointment to confirm or reject. Please enter an "
                                                     "appointment's row number:")

                # choose accept or reject or back
                further_options = ["Confirm", "Reject", "Back"]
                selected = ui.ask_choice("What would you like to do with this appointment?", choices=further_options)
                if selected == "Back":  # back
                    res = None  # remove result to exit from while loop if back chosen
                    self.to_confirm_appointments()
                elif selected == "Confirm":  # accept
                    success = util.db_update([selected_row], "appointment", "appointment_id", **{"is_confirmed": 1})
                    if success:
                        ui.info(ui.green,
                                f"Appointment on {selected_row['date']} with {selected_row['patient name']} successfully confirmed. Sending status update email to patient in background.")
                        #  send email of confirmation.
                        util.create_thread_task(util.send_appt_confirmation_email,
                                                function_arguments_tuple=(selected_row['appointment_id'], True))

                    else:
                        ui.info("There was an error, processing your request, please try later")
                elif selected == "Reject":  # reject
                    success = util.db_update([selected_row], "appointment", "appointment_id", **{"is_rejected": 1})
                    if success:
                        ui.info(ui.green,
                                f"Appointment on {selected_row['date']} with {selected_row['patient name']} successfully rejected. Sending status update email to patient in background.")
                        # SEND EMAIL TO PATIENT NOTIFYING OF REJECTED APPT
                        util.create_thread_task(util.send_appt_confirmation_email,
                                                function_arguments_tuple=(selected_row['appointment_id'], False))
                    else:
                        ui.info("There was an error, processing your request, please try later")

            else:
                res = None  # remove result to exit from while loop if back chosen
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
        util.sys_clear()

        # state variables
        self.curr_appt_id = None  # reset current appointment if previously declared
        self.patient_id = None
        self.prev_appt_records = None

        appt_date = self.curr_appt_date

        ui.info_section(ui.blue, "View your appointments")
        # instructions
        ui.info(ui.faint, "Info:"
                          "\nDefault view will show your appointments for today."
                          "\nIf you have any appointments, select one to view the appointment details: add "
                          "prescriptions, referrals, clinical notes, view a patients previous appointment history "
                          "etc.\n")

        ui.info(f"showing appointments for {str(appt_date)}")
        if appt_date == "today":
            date = "date('now')"
        else:
            date = f"'{appt_date}'"
        # get appointments for the GP user
        get_appts_sql_query = "SELECT appointment_id,  u.firstName || ' ' || u.lastName as 'patient name',  strftime(" \
                              f"'%d/%m/%Y', " \
                              f"s.starttime) as date, strftime('%H:%M', s.starttime)  as 'appointment time' FROM " \
                              f"APPOINTMENT  a " \
                              f"left join Users u " \
                              f" on u.userId = a.patient_id left join slots s on s.slot_id = a.slot_id WHERE " \
                              f"IS_CONFIRMED= 1 and  " \
                              f"GP_ID = {self.user_id}  and date(s.starttime) = {date} order by s.starttime "

        res = self.db.fetch_data(get_appts_sql_query)

        # if date is in past the had, else have
        try:
            if datetime.strptime(appt_date, '%Y-%m-%d').date() < datetime.today().date():
                tense = "had"
            else:
                tense = "have"
        except ValueError:
            # if date is 'today'
            tense = "have"
        ui.info_2(ui.standout, f"{appt_date} - you {tense} {len(res)} appointment(s)")

        # show appts table
        if res:
            table_data = util.output_sql_rows(res, ["date", "appointment time", "patient name"])
            print(table_data)
            selected = util.user_select("What would you like to do?", choices=self.state_gen.get_state_options())
            if selected == "Select an appointment":
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
            #  LOG ERROR IF INVALID DICTIONARY PASSED TO FUNCTION.
            logging.exception("Exception occurred.")
            ui.info(ui.red, "An error has occurred. We could not get the appointment data for the record.")
            ui.info("Going back to 'view appointment' page")
            util.loading()
            self.handle_state_selection("back")

    def show_appointment_details(self):
        util.sys_clear()

        appt_id = self.curr_appt_id  # grab state variable of current appointment

        # print appt summary - details, patient, reason, clinical notes, prescriptions, referrals etc.
        util.print_appointment_summary(appt_id)

        # offer options for this state (write/edit notes, prescriptions, referals, finalise appt, view patient records.)
        selected = util.user_select("How would you like to proceed?", self.state_gen.get_state_options())
        if selected == "Write prescriptions":
            self.to_write_prescriptions(appt_id)  # handle manually as state requires appt_id argument
        elif selected == "Back":  # need to skip select appointment
            self.to_view_my_appointments()
        else:
            self.handle_state_selection(selected)

    def write_clinical_notes(self):
        appt_id = self.curr_appt_id

        too_early_query = f"SELECT date(s.starttime) > date('now') as is_after_now FROM APPOINTMENT LEFT JOIN SLOTS S " \
                          f"USING (SLOT_ID) where appointment_id = {self.curr_appt_id}"
        too_early = self.db.fetch_data(too_early_query)
        too_early = too_early[0]["is_after_now"]

        if too_early == 1:
            ui.warning("This appointment is in the future.")
            proceed = ui.ask_yes_no("Are you sure you would like to proceed?")
            if not proceed:
                ui.info("Returning to previous screen.")
                util.loading()
                self.handle_state_selection("back")

        # get clinical notes for this appt
        clinical_notes_query = f"SELECT clinical_notes, appointment_id from Appointment where appointment_id = {appt_id}"
        clinical_notes = self.db.fetch_data(clinical_notes_query)

        rewrite_or_append = ""  # declaring choice variable for if a patient already has notes.

        # if clinical notes not null, does user want to rewrite or append to clinical notes.
        if clinical_notes[0]["clinical_notes"] is not None:
            ui.info("There are already notes for this appointment:")
            ui.info_2(f"Clinical notes: \n", ui.indent(clinical_notes[0]['clinical_notes'], 6))
            user_options = ["append to current notes", "rewrite clinical notes (overwrite)", "back"]
            rewrite_or_append = util.user_select("What would you like to do?", choices=user_options)
            if rewrite_or_append == "back":
                self.handle_state_selection(rewrite_or_append)
            else:
                ui.info_1(ui.standout, f"Mode: {rewrite_or_append}")
        else:
            ui.info(ui.standout, "Begin writing clinical notes.")

        # multi line input
        notes = util.get_multi_line_input("Please write your clinical notes here:")

        if rewrite_or_append == "append to current notes":  # if append need to append.
            notes = "\n".join([clinical_notes[0]["clinical_notes"], notes])
            ui.info_1("We've appended your new notes to the previous notes:")
        else:
            ui.info_1("Your clinical notes:")

        # replace any invalid double quotation marks with single.
        notes = notes.replace('"', '\'')

        ui.info(ui.indent(notes, 6))
        if ui.ask_yes_no(
                "Are you happy to add the clinical notes to the appointment? Select 'No' to discard changes or 'Yes' "
                "to save."):
            # update db
            try:
                success = util.db_update(clinical_notes, "Appointment", "appointment_id",
                                         **{"clinical_notes": f'"{notes}"'})
            except OperationalError:
                logging.exception(
                    f"Exception occurred when updating clinical notes in DB. notes value entered = {notes}")
                ui.error("an error occurred while updating the database. Change not saved. Please try again later.")
                ui.info("Returning to appointment details")
                util.loading()
                # Return to Appointment details
                self.to_show_appointment_details()

            if success:
                ui.info(ui.green, "Clinical notes successfully saved.")
            else:
                ui.info("There was an error, processing your request, please try later")
            ui.info("Returning to appointment details")
            util.loading()
            # Return to Appointment details
            self.to_show_appointment_details()
        else:
            # go back or rewrite?
            options = ["Try writing clinical notes again", "back"]
            selected = util.user_select("What would you like to do now?", choices=options)
            if selected == "Back":
                self.handle_state_selection("back")
            else:
                self.to_write_clinical_notes()  # restart state from scratch if gp wants to try writing again.

    def write_prescriptions(self, appt_id):
        # check if this appt is in the future, if so stop GP from adding. return to previous screen.
        too_early_query = f"SELECT date(s.starttime) > date('now') as is_after_now FROM APPOINTMENT LEFT JOIN SLOTS S " \
                          f"USING (SLOT_ID) where appointment_id = {self.curr_appt_id}"
        too_early = self.db.fetch_data(too_early_query)
        too_early = too_early[0]["is_after_now"]

        if too_early == 1:
            ui.warning("Sorry, prescriptions cannot be written for appointments in the future. \nPrescriptions may be "
                       "written for appointments today, or amended for appointments in the past.")
            ui.info("Returning to previous screen")
            util.loading(load_time=4)
            self.handle_state_selection("back")

        # otherwise all ok, continue with prescription flow.

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
                #  log error
                logging.exception(
                    f"Exception occurred when saving prescription to database. insert stmt = {prescription_insert_stmt}")
                ui.error("Sorry, an error occurred when saving. Please try again later.")

        user_options = ["write another prescription", "back"]
        selected = util.user_select("How would you like to proceed?", choices=user_options)
        if selected == "Write another prescription":
            self.to_write_prescriptions(appt_id)
        elif selected == "Back":
            self.to_show_appointment_details()

    def add_referral(self):
        util.sys_clear()
        appt_id = self.curr_appt_id  # get current state appointment id

        ui.info_section("Refer this patient to a specialist")

        # if referral already populated. This will be overwritten, by continuing. Proceed? or back?
        referral_check_query = f"SELECT referred_specialist_id, 'Dr '||s.firstName||' '||s.lastName as doc_name, " \
                               f"s.hospital, d.name as dept_name FROM APPOINTMENT a left join Specialists " \
                               f"s on s.specialist_id = " \
                               f"a.referred_specialist_id left join Department d on d.department_id = s.department_id " \
                               f"WHERE appointment_id= " \
                               f"{appt_id} "
        referral_check = self.db.fetch_data(referral_check_query)
        if referral_check[0]["referred_specialist_id"] is not None:
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
        referral_cat_table = util.output_sql_rows(referral_cats, ["name"], ["department name"])
        ui.info("Referral departments:")
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

    def finalise_appointment(self):
        util.sys_clear()
        appt_id = self.curr_appt_id

        too_early_query = f"SELECT date(s.starttime) > date('now') as is_after_now FROM APPOINTMENT LEFT JOIN SLOTS S " \
                          f"USING (SLOT_ID) where appointment_id = {self.curr_appt_id}"
        too_early = self.db.fetch_data(too_early_query)
        too_early = too_early[0]["is_after_now"]

        if too_early == 1:
            ui.warning("This appointment is in the future.")
            proceed = ui.ask_yes_no("Are you sure you would like to proceed?")
            if not proceed:
                ui.info("Returning to previous screen.")
                util.loading()
                self.handle_state_selection("back")

        # appointment status summary - clinical notes written? prescription? referral?
        util.print_appointment_summary(appt_id)

        check_populated_query = f"SELECT clinical_notes, referred_specialist_id, appointment_id from appointment " \
                                f"where appointment_id = {appt_id} "
        check_prescription_query = f"SELECT * FROM prescription where appointment_id = {appt_id}"

        check_populated = self.db.fetch_data(check_populated_query)
        check_prescription = self.db.fetch_data(check_prescription_query)

        if check_populated[0]["clinical_notes"] is None:
            notes_status = "No notes added."
            notes_colour_status = ui.red
            confirmation_message = "No notes have been added. It would be against standard procedure to finalise an " \
                                   "appointment without any clinical notes. \nAre you sure you would like to continue?"
        else:
            notes_status = "Notes added."
            notes_colour_status = ui.green
            confirmation_message = "Recommended fields populated. Status is OK. Are you happy to continue?"

        if len(check_prescription) == 0:  # empty - no prescriptions
            prescription_status = f"No prescription needed."
        else:
            prescription_status = f"{len(check_prescription)} prescription(s) added."

        if check_populated[0]["referred_specialist_id"] is None:
            referred_status = "No referral necessary."
        else:
            referred_status = "Referral necessary - patient referred to specialist."

        # summarise completion of appt details
        ui.info_1(ui.underline, "Finalise this appointment")
        ui.info_2("Status summary:")
        ui.info(ui.indent("Clinical notes:", 6), notes_colour_status, f"{notes_status}")
        ui.info(ui.indent(f"Prescription: {prescription_status}", 6))
        ui.info(ui.indent(f"Referral: {referred_status}", 6))

        # Finalisation confirmation flow.
        print("\n")
        ui.info_count(0, 3, "Finalisation process")
        if ui.ask_yes_no(notes_colour_status, confirmation_message):
            ui.info_count(1, 3, "Finalisation process")
            new_options = ["Yes", "No", "Abort finalisation process"]
            selected = util.user_select("Should this patient be emailed the appointment details?", choices=new_options)
            if selected == "Abort finalisation process":
                self.handle_state_selection("back")
            elif selected == "Yes":
                email = True
            elif selected == "No":
                email = False

            # perform update is_completed = 1 in appointment table.
            success = util.db_update(check_populated, "Appointment", "appointment_id", **{"is_completed": 1})
            if success:
                util.loading(load_time=2, new_line=False)
                ui.info_3(" Appointment marked as finalised.")
            else:
                ui.error("There was an error, processing your request, please try later")
                ui.info("Returning to appointment page.")
                util.loading()
                self.to_show_appointment_details()

            # send email or not of appt details
            try:
                if email:
                    ui.info_3("Sending email... please wait...")
                    util.email_appt_summary(appt_id)
                    util.loading(load_time=2, new_line=False)
                    ui.info_3(" Email sent to patient")
                else:
                    # don't send email
                    util.loading(load_time=2, new_line=False)
                    ui.info_3(" Email not sent to patient")
            except UnboundLocalError:
                # logging
                logging.exception("Exception occurred while finalising appt email.")
                print(
                    "An error occurred. The patient may not have been emailed successfully if this option was chosen.")

            util.loading(load_time=2, new_line=False)
            ui.info_count(2, 3, "Finalisation process complete")
        else:
            selected = util.user_select("Go back to the appointment page to make amends to this consultation and "
                                        "abort the "
                                        "finalisation process.", choices=self.state_gen.get_state_options())
            self.handle_state_selection(selected)
        # Return to main options.
        if ui.ask_yes_no("Return to 'view my appointments' page?"):
            util.loading(load_time=2)
            self.to_view_my_appointments()
        else:
            selected = util.user_select("No where else to go from here...", choices=self.state_gen.get_state_options())
            self.handle_state_selection(selected)

    def view_patient_medical_history(self):
        util.sys_clear()
        # check how many records are available
        appt_id = self.curr_appt_id
        # use appt_id to get patient_id
        get_patient_records_query = f"SELECT * FROM appointment left join slots s using (slot_id) where patient_id = " \
                                    f"(select patient_id from " \
                                    f"appointment where appointment_id = {appt_id}) and date(s.endTime) < date('now') " \
                                    f"and is_completed = 1 order by " \
                                    f"slot_id asc "
        get_patient_records = self.db.fetch_data(get_patient_records_query)

        patient_id_query = f"select patient_id from appointment where appointment_id = {appt_id}"
        patient_id_fetch = self.db.fetch_data(patient_id_query)
        self.patient_id = patient_id_fetch[0]["patient_id"]

        get_medical_hist_query = f"SELECT * from MedicalHistory where UserID = {self.patient_id}"
        get_medical_hist = self.db.fetch_data(get_medical_hist_query)

        # general medical history info if any on record.
        ui.info_section(ui.blue, "View Patient Medical History\n")
        ui.info(ui.bold, "General Medical History:")
        if len(get_medical_hist) == 0:
            ui.info(ui.indent("No known medical conditions for this patient."))
        else:
            # if there is medical history, print out table showing data.
            med_hist_table = util.output_sql_rows(get_medical_hist,
                                                  ["illness", "time_afflicted", "description", "prescribed_medication"],
                                                  ["illness", "time afflicted", "description", "prescribed medication"])
            print(med_hist_table)

        # if no prev records available, only go back.
        ui.info(ui.bold, "\nPrevious appointment records:")
        if len(get_patient_records) == 0:  # i.e. no previous records
            ui.info(ui.indent("No previous appointments for this patient on the system."))
            selected = util.user_select("Return to home screen:", ["Back"])
            self.handle_state_selection(selected)
        else:
            # if available - "patient has X records from previous appointments available"
            ui.info(ui.indent(
                f"Records on the system from previous appointments available to view: {len(get_patient_records)}"))
            self.prev_appt_records = get_patient_records  # set state variable for future states if prev appt data
            # needed
            # show options - view previous appointment records, back
            selected = util.user_select("\nWhat would you like to do?", choices=self.state_gen.get_state_options())
            self.handle_state_selection(selected)

    def view_previous_appointment_records(self):
        # "there are X no. records"  - option: select a number to view by recency OR download full history OR back
        ui.info_section(ui.blue, "View previous appointment records")
        ui.info_2(f"{len(self.prev_appt_records)} record(s) available to view.")

        # options
        selected = util.user_select("How would you like to view these records?", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def view_patient_records_by_recency(self):
        # give option to choose limit on sql query order by date desc
        limit_chosen = False
        valid_numbers = [x + 1 for x in range(len(self.prev_appt_records))]
        while not limit_chosen:
            limit_number = ui.ask_string(
                f"Please enter how many records you would like to view (total records:{len(self.prev_appt_records)}):")
            try:
                limit_number = int(limit_number)
                if limit_number in valid_numbers:
                    limit_chosen = True
                else:
                    ui.info("Please enter a number equal to or less than the number of total records.")
            except ValueError:
                ui.info("Please enter a number.")

        # get results.
        ui.info(f"Fetching {limit_number} results in order of appointment date")
        util.loading()
        util.sys_clear()
        ui.info_section(ui.blue, "Viewing patient medical records by recency")
        for i in range(limit_number):
            # get each appointment up to index - results already ordered.
            desired_index = len(self.prev_appt_records) - limit_number + i  # results are in time asc, we want to print
            # most recent results with latest as last printed for the number chosen
            util.print_appointment_summary(self.prev_appt_records[desired_index]["appointment_id"])

        selected = util.user_select("What would you like to do next?", choices=self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def download_all_records_as_a_csv(self):
        get_patient_name_query = f"SELECT firstname || ' ' || lastname as patient_name, firstname || '_' || lastname " \
                                 f"as p_name_underscore from users where userid = {self.patient_id} "
        get_patient_name = self.db.fetch_data(get_patient_name_query)
        patient_name = get_patient_name[0]["patient_name"]
        name_no_spaces = get_patient_name[0]["p_name_underscore"]

        # confirmation
        if ui.ask_yes_no(f"Please confirm you would like to download appointment history records for {patient_name}"):
            try:
                ui.info(ui.ellipsis, "Downloading data")
                ui.info_count(0, 3, "Fetching data from database")
                # CSV
                curr_dir = os.path.abspath(os.getcwd())
                dir_name = "downloaded_data"

                # check file path and directory exists, if not create it
                save_path = os.path.join(curr_dir, dir_name)
                if not os.path.exists(save_path):
                    os.makedirs(save_path)

                csv_filename = f"patient_records_{name_no_spaces}_{datetime.today().strftime('%Y%m%d')}.csv"

                csv_file = os.path.join(save_path, csv_filename)
                print(csv_file)

                full_records_query = f"select u.firstName || ' ' || u.lastname as patient_name, u.date_of_birth as " \
                                     f"patient_dob, u2.firstName || ' ' || u2.lastname as doctor_seen, starttime as " \
                                     f"appt_time, reason, clinical_notes, medicine_name, treatment_description, " \
                                     f"pres_frequency_in_days, startDate as prescription_startDate, expiryDate as " \
                                     f"prescription_expiryDate, " \
                                     f"sp.firstName || ' '|| sp.lastName as referred_specialist, hospital as " \
                                     f"referred_hospital, d.name as referred_dept_name from Appointment a left join " \
                                     f"Slots s using (slot_id) left join Prescription p on p.appointment_id = " \
                                     f"a.appointment_id left join Specialists sp on sp.specialist_id = " \
                                     f"a.referred_specialist_id left join users u on a.patient_id = u.userId left join " \
                                     f"Users u2 on a.gp_id = u2.userId left join Department d on d.department_id = " \
                                     f"sp.department_id where patient_id = {self.patient_id} and date(s.endTime) " \
                                     f"<date('now') and is_completed = 1 order by slot_id asc"
                full_records = self.db.fetch_data(full_records_query)
                ui.info_count(1, 3, "Creating CSV file")
                ui.info_count(2, 3, "Inserting medical record data")

                with open(csv_file, "w") as records_csv:
                    csv_writer = csv.DictWriter(records_csv, fieldnames=full_records[0].keys())
                    csv_writer.writeheader()
                    for row in full_records:
                        csv_writer.writerow(row)

                ui.info_2(
                    "CSV saved successfully. Please check the downloaded_data folder in the application directory. ("
                    f"full path - {csv_file})")
                ui.info("Returning to previous screen")
                util.loading()
                self.handle_state_selection("back")

            except IOError:
                logging.exception("Exception occurred fetching and saving data as CSV:")
                ui.error("Sorry, an error occurred while saving the data as a CSV")
                ui.info("Returning to previous screen")
                util.loading()
                self.handle_state_selection("back")
        else:  # if download not confirmed.
            ui.info("Returning to previous screen")
            util.loading()
            self.handle_state_selection("back")

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
