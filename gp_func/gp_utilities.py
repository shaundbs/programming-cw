import logging
import re
import threading  # send emails in background
from datetime import datetime
from time import sleep
from os import system

import cli_ui as ui
from pick import pick
from tabulate import tabulate

from . import gp_database as db
from .gp_email_generator import Emails


# utility functions for the GP flow


def user_select(prompt: str, choices: list):
    selected = None
    while selected is None:
        # try:  # if terminal can support, then cursor selection.
        #     choice, index = pick(choices, prompt + " (use arrow keys)", indicator='=>')
        #     selected = choice
        # except Exception as err:
        # log error
        # logging.info("Exception occurred while trying to use cursors for user input.")
        try:
            selected = ui.ask_choice(prompt, choices=choices, sort=False)
        except AttributeError:
            print("Please choose a valid option.")
    return selected


def output_sql_rows(query_result, column_names: list, table_headers=None, table_format="grid"):
    """
    Takes a list of nested dictionaries as input and returns a table with row numbers
    :param table_format: table formatting
    :param query_result: sql result
    :param column_names: column names in query result to output in the table
    :param table_headers: names of header columns - should map to column names given
    :return: table that can be printed
    """
    if table_headers is None:
        table_headers = []
    output_list = []
    if table_headers:
        table_headers.insert(0, "row")
        output_headers = table_headers
    else:
        cols_copy = column_names.copy()
        cols_copy.insert(0, "row")
        output_headers = cols_copy
    output_list.append(output_headers)
    for row, values in enumerate(query_result, start=1):
        record = [row]
        for header in column_names:  # skip initial header i.e. row header
            record.append((values[header]))
        output_list.append(record)
    # return Table(output_list, table_title).table
    return tabulate(output_list, headers="firstrow", tablefmt=table_format)


def db_update(record_list, table_name, pk_column_name, **new_column_values):
    # unpack columns to set
    update_columns = "set "
    for index, col in enumerate(new_column_values):
        if index == len(new_column_values) - 1:
            update_columns += f"{col}= {new_column_values[col]} "
        else:
            update_columns += f"{col}= {new_column_values[col]}, "

    # get primary key values from records_list to update those rows.
    pk_values = []
    pk_placeholder = "( "
    for i in range(len(record_list)):
        if i == len(record_list) - 1:
            pk_placeholder += "?)"
            pk_values.append(record_list[i][pk_column_name])
        else:
            pk_placeholder += "?, "
            pk_values.append(record_list[i][pk_column_name])

    update_sql = f"update {table_name} " + update_columns + f"where {pk_column_name} in " + pk_placeholder
    err = db.Database().exec_one(update_sql, tuple(pk_values))
    if err is None:
        return True
    else:
        logging.error(f"Error occurred during gp db_update: \n{err}")
        return False


def select_table_row(result_list, table, user_prompt: str):
    """
    Takes a list with records/rows as nested dictionaries, a table to show user, and handles user selection of a table row.
    :param result_list: list of records, with each row as a nested dictionary.
    :param table: terminal table ascii table
    :param user_prompt: what to ask the user to do
    :return: dictionary of the selected row
    """
    print(table)
    choice = ""
    valid_choices = [x for x in range(len(result_list))]
    while choice not in valid_choices:
        try:
            choice = ui.ask_string(user_prompt)
            choice = int(choice) - 1  # to match index
            selected_row = result_list[choice]
        except ValueError:
            print("Please enter a number.")
        except IndexError:
            print("PLease enter a valid number found in the row column of the table.")
        except TypeError:
            print("Please enter a number.")
    return selected_row


def loading(load_time=3, new_line=True):
    """
    Display dot, then sleep
    :param new_line: whether to add a new line after loading finishes.
    :param load_time: load_time * 0.8 seconds = how long to display loading screen.
    :return:
    """
    for i in range(load_time - 1):
        ui.dot()
        sleep(0.8)
    if new_line:
        ui.dot(last=True)
    else:
        ui.dot()


def get_user_date():
    """
    triggers user input to enter a valid date 'YYYY-MM-DD' validated via regex.
    """
    date_not_valid = True
    while date_not_valid:

        selected_date = ui.ask_string("Please enter a date in the format YYYY-MM-DD:")
        try:
            # date validation. Can be any date if in valid format.
            if selected_date.strip().lower() == "today":
                selected_date = datetime.today().strftime('%Y-%m-%d')
            date_to_search = re.search("^\d\d\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])$", selected_date.strip())
            if date_to_search is None:  # no match found
                ui.info(ui.red, "No valid date found in input. Please enter a valid date YYYY-MM-DD with no spaces.")
            else:
                date_to_search = date_to_search.group()
                datetime.strptime(date_to_search, '%Y-%m-%d')
                date_not_valid = False
                return date_to_search
        except AttributeError:
            print("No date entered")
        except ValueError:
            print("Day is outside the range of the selected month")


def get_user_month():
    """
    """
    date_not_valid = True
    while date_not_valid:

        selected_date = ui.ask_string("Please enter a date in the format YYYY/MM:")
        # date validation. Can be any date if in valid format.
        try:
            if selected_date.strip().lower() == "today":
                selected_date = datetime.today().strftime('%Y/%m')
            date_to_search = re.search("^\d\d\d\d[/](0[1-9]|1[012])$", selected_date.strip())
            if date_to_search is None:  # no match found
                ui.info(ui.red, "No valid date found in input. Please enter a valid date YYYY/MM with no spaces.")
            else:
                date_to_search = date_to_search.group()
                date_not_valid = False
                return date_to_search
        except AttributeError:
            print("No date entered")


def get_multi_line_input(user_prompt):
    """
    Gets multi line input from user.
    :param user_prompt: Str to prompt user with
    :return:
    """
    # loop input fields until user enters q to quit/exit
    ui.info(user_prompt)
    ui.info_2("This is a multi-lined input. Use [Enter] to start a new line.")
    ui.info_2(ui.bold, "Enter 'q', 'quit' or 'exit' on a new line to finish the entry.")
    exit_inputs = ['q', 'quit', 'exit']

    inputs = []
    while True:
        new_value = input()
        if new_value in exit_inputs:
            break
        else:
            inputs.append(new_value)

    # if any input field over x characters, we will split it to display correctly in the terminal.
    formatted_inputs = []
    for input_text in inputs:
        # print(input_text)
        # search for the first space above x characters and split.
        current_index = 0
        count_char = 0
        last_cut = 0
        for char in input_text:
            # print(char, current_index, count_char, last_cut)
            if len(input_text) == current_index + 1:  # if last element
                formatted = input_text[last_cut:]
                formatted_inputs.append(formatted)
            elif char == ' ' and count_char > 70:
                formatted = input_text[last_cut:count_char + 1]
                formatted_inputs.append(formatted)
                last_cut = count_char + 1
                count_char = 0
            count_char += 1
            current_index += 1
    return "\n".join(formatted_inputs)


def sys_clear():
    _ = system('cls||clear')


def print_appointment_summary(appt_id):
    conn = db.Database()
    get_apt_details_query = f"SELECT appointment_id,  u.firstName || ' ' || u.lastName as 'patient name',  " \
                            f"strftime('%d/%m/%Y', s.starttime) as date, strftime('%H:%M', s.starttime)  as " \
                            f"'appointment time', reason, referred_specialist_id, clinical_notes FROM APPOINTMENT " \
                            f" a left join Users u on u.userId = " \
                            f"a.patient_id left join slots s on s.slot_id = a.slot_id WHERE appointment_id= " \
                            f"{appt_id} "
    appt_details = conn.fetch_data(get_apt_details_query)

    # Prescription
    prescription_query = f"select * from Prescription where appointment_id = {appt_id}"
    prescription_data = conn.fetch_data(prescription_query)

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
    if appt_details[0]["clinical_notes"] is None:
        clinical_notes = "No notes added yet."
    else:
        clinical_notes = appt_details[0]["clinical_notes"]
    ui.info(ui.bold, "Clinical Notes:\n", ui.indent(clinical_notes, 4), "\n")

    # Prescriptions
    if len(prescription_data) == 0:
        ui.info(ui.bold, "Prescriptions:", ui.reset, "None prescribed yet.\n")
    else:
        columns = ["medicine_name", "treatment_description", "pres_frequency_in_days", "startDate", "expiryDate"]
        headers = ["Medicine", "Treatment", "Repeat prescription (days)", "Start date", "Prescription valid until"]
        pres_table = output_sql_rows(prescription_data, columns, headers)
        ui.info(ui.bold, "Prescriptions:")
        print(pres_table, "\n")

    # Referrals
    if appt_details[0]["referred_specialist_id"] is None:
        ui.info(ui.bold, "Referral:", ui.reset, "No referral added.\n")
    else:
        # Need to grab info from db for referral.
        referral_query = f"SELECT 'Dr '||firstName||' '||lastName as doc_name, hospital, specialist_id, d.name as " \
                         f"dept_name from Specialists left join Department d using(department_id) where " \
                         f"specialist_id = {appt_details[0]['referred_specialist_id']} "
        referral = conn.fetch_data(referral_query)
        ui.info(ui.bold, "Referral:", ui.reset,
                f"{referral[0]['dept_name']} department - {referral[0]['doc_name']} at {referral[0]['hospital']}.\n")


# create tasks to run in parallel / background
def create_thread_task(function_to_call, function_arguments_tuple):
    task = threading.Thread(target=function_to_call, args=function_arguments_tuple, daemon=True)
    task.start()


def email_appt_summary(appt_id):
    # get appt info for patient text

    conn = db.Database()
    get_apt_details_query = f"SELECT appointment_id, u.email as 'patient email', u.firstName || ' ' || u.lastName as " \
                            f"'patient name',  " \
                            f"strftime('%d/%m/%Y', s.starttime) as date, strftime('%H:%M', s.starttime)  as " \
                            f"'appointment time', reason, referred_specialist_id, clinical_notes, 'Dr' || ' ' || " \
                            f"u1.firstName || ' ' || u1.lastName as 'doctor name' FROM APPOINTMENT " \
                            f" a left join Users u on u.userId = " \
                            f"a.patient_id left join Users u1 on u1.userID = a.gp_id left join slots s on s.slot_id = " \
                            f"a.slot_id WHERE appointment_id= " \
                            f"{appt_id} "
    appt_details = conn.fetch_data(get_apt_details_query)

    # Prescription
    prescription_query = f"select * from Prescription where appointment_id = {appt_id}"
    prescription_data = conn.fetch_data(prescription_query)

    # Base details
    if appt_details[0]['reason'] is None:
        reason = "Not specified"
    else:
        reason = appt_details[0]['reason']

    # Clinical notes
    if appt_details[0]["clinical_notes"] is None:
        clinical_notes = "No notes added yet."
    else:
        clinical_notes = appt_details[0]["clinical_notes"]

    email_text = ["Appointment Information:", f"Appointment date: {appt_details[0]['date']}",
                  f"Appointment time: {appt_details[0]['appointment time']}",
                  f"Patient Name: {appt_details[0]['patient name']}", f"Reason for appointment: {reason} \n",
                  f"Doctor seen: {appt_details[0]['doctor name']}", f"Clinical Notes:\n{clinical_notes}"]

    if len(prescription_data) == 0:
        email_text.append("Prescriptions: None prescribed yet.\n")
    else:
        columns = ["medicine_name", "treatment_description", "pres_frequency_in_days", "startDate", "expiryDate"]
        headers = ["Medicine", "Treatment", "Repeat prescription (days)", "Start date", "Prescription valid until"]
        email_text.append("Prescriptions:")
        email_text.append(output_sql_rows(prescription_data, columns, headers, table_format="html"))

    # Referrals
    if appt_details[0]["referred_specialist_id"] is None:
        email_text.append(f"Referral: No referral added.")
    else:
        # Need to grab info from db for referral.
        referral_query = f"SELECT 'Dr '||firstName||' '||lastName as doc_name, hospital, specialist_id, d.name as " \
                         f"dept_name from Specialists left join Department d using(department_id) where " \
                         f"specialist_id = {appt_details[0]['referred_specialist_id']} "
        referral = conn.fetch_data(referral_query)
        email_text.append(
            f"Referral: {referral[0]['dept_name']} department - {referral[0]['doc_name']} at {referral[0]['hospital']}.")

    summary_text_plain = "\n".join(email_text)
    summary_text_html = "<br>".join(email_text)

    # get patient email + patient name
    email = appt_details[0]['patient email']
    patient = appt_details[0]['patient name']

    Emails.appointment_summary_email(email, patient, summary_text_plain, summary_text_html)


def send_appt_confirmation_email(appt_id, confirmed=True):
    """

    :param appt_id:
    :param confirmed: True is appt confirmed, False if rejected.
    :return:
    """
    conn = db.Database()
    get_apt_details_query = f"SELECT appointment_id, u.email as 'patient email', u.firstName || ' ' || u.lastName as " \
                            f"'patient name',  " \
                            f"strftime('%d/%m/%Y', s.starttime) as date, strftime('%H:%M', s.starttime)  as " \
                            f"'appointment time', reason, referred_specialist_id, clinical_notes, 'Dr' || ' ' || " \
                            f"u1.firstName || ' ' || u1.lastName as 'doctor name' FROM APPOINTMENT " \
                            f" a left join Users u on u.userId = " \
                            f"a.patient_id left join Users u1 on u1.userID = a.gp_id left join slots s on s.slot_id = " \
                            f"a.slot_id WHERE appointment_id= " \
                            f"{appt_id} "
    appt_details = conn.fetch_data(get_apt_details_query)

    if appt_details[0]['reason'] is None:
        reason = "Not specified"
    else:
        reason = appt_details[0]['reason']

    email_text = []

    if confirmed:
        email_text.append(f"Great news. You're appointment on {appt_details[0]['date']} has been confirmed.")
        status = "confirmed"
    else:
        email_text.append(f"We regret to inform you that you're appointment on {appt_details[0]['date']} has been "
                          f"cancelled by the GP. Please log back in to book again or reschedule. Sorry for any "
                          f"inconvenience caused.")
        status = "cancelled"

    email_text.append("\n")

    email_text.append("This appointment's details:")

    email_text += [f"Status: {status}", "Appointment Information:", f"Appointment date: {appt_details[0]['date']}",
                   f"Appointment time: {appt_details[0]['appointment time']}",
                   f"Patient Name: {appt_details[0]['patient name']}", f"Reason for appointment: {reason} \n",
                   f"Doctor: {appt_details[0]['doctor name']}"]

    summary_text_plain = "\n".join(email_text)
    summary_text_html = "<br>".join(email_text)

    # get patient email + patient name
    email = appt_details[0]['patient email']
    patient = appt_details[0]['patient name']

    Emails.appointment_confirmation_email(email, patient, summary_text_plain, summary_text_html)
