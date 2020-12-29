from pick import pick
import cli_ui as ui
from terminaltables import AsciiTable as Table
import gp_database as db
from time import sleep
import re
from datetime import datetime
import calendar


# utility functions for the GP flow


def user_select(prompt: str, choices: list):
    # try:  # if terminal can support, then cursor selection.
    #     choice, index = pick(choices, title)
    #     return choice
    # except Exception:
    selected = ui.ask_choice(prompt, choices=choices, sort=False)
    return selected


def output_sql_rows(query_result, column_names: list, table_headers=[], table_title=None):
    """
    Takes a list of nested dictionaries as input and returns a terminaltable Asciitable
    :param query_result: sql result
    :param column_names: column names in query result to output in the table
    :param table_headers: names of header columns - should map to column names given
    :param table_title: title of the table
    :return: terminaltable Asciitable that can be printed
    """
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
    return Table(output_list, table_title).table


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
        # TODO: log the error
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
    return selected_row


def loading(load_time=3):
    """
    Display dot, then sleep
    :param load_time: load_time * 0.8 seconds = how long to display loading screen.
    :return:
    """
    for i in range(load_time - 1):
        ui.dot()
        sleep(0.8)
    ui.dot(last=True)


def get_user_date():
    """
    triggers user input to enter a valid date 'YYYY-MM-DD' validated via regex.
    """
    date_not_valid = True
    while date_not_valid:

        selected_date = ui.ask_string("Please enter a date in the format YYYY-MM-DD:")
        # date validation. Can be any date if in valid format.
        if selected_date.strip().lower() == "today":
            selected_date = datetime.today().strftime('%Y-%m-%d')
        date_to_search = re.search("^\d\d\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])$", selected_date.strip())
        if date_to_search is None:  # no match found
            ui.info(ui.red, "No valid date found in input. Please enter a valid date YYYY-MM-DD with no spaces.")
        else:
            date_to_search = date_to_search.group()
            date_not_valid = False
            return date_to_search

            # if ui.ask_yes_no(f"Search for appointments on {date_to_search}?"):
            #     date_not_valid = False


def get_user_month():
    """
    """
    date_not_valid = True
    while date_not_valid:

        selected_date = ui.ask_string("Please enter a date in the format YYYY/MM:")
        # date validation. Can be any date if in valid format.
        if selected_date.strip().lower() == "today":
            selected_date = datetime.today().strftime('%Y/%m')
        date_to_search = re.search("^\d\d\d\d[/](0[1-9]|1[012])$", selected_date.strip())
        if date_to_search is None:  # no match found
            ui.info(ui.red, "No valid date found in input. Please enter a valid date YYYY/MM with no spaces.")
        else:
            date_to_search = date_to_search.group()
            date_not_valid = False
            return date_to_search


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


def print_appointment_summary(appt_id):
    conn = db.Database()
    get_apt_details_query = f"SELECT appointment_id,  u.firstName || ' ' || u.lastName as 'patient name',  " \
                            f"strftime('%d/%m/%Y', s.starttime) as date, strftime('%H:%M', s.starttime)  as " \
                            f"'appointment time', reason, referred_specialist_id, clinical_notes FROM APPOINTMENT " \
                            f" a left join Users u on u.userId = " \
                            f"a.patient_id left join slots s on s.slot_id = a.slot_id WHERE appointment_id= " \
                            f"{appt_id} "
    appt_details = conn.fetch_data(get_apt_details_query)
    # todo: add check that there is only one record returned. if not == problem

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
        pres_table = output_sql_rows(prescription_data, columns, headers, table_title="Prescriptions")
        print(pres_table)

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
