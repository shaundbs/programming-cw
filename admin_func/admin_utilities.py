import cli_ui as ui
import re
from pandas import DataFrame
from tabulate import tabulate


def user_select(prompt: str, choices: list):
    selected = None
    while selected is None:
        # try:  # if terminal can support, then cursor selection.
        #     choice, index = pick(choices, prompt)
        #     selected = choice
        # except Exception as err:
        #     # log error
        #     logging.info("Exception occurred while trying to use cursors for user input.")
        try:
            selected = ui.ask_choice(prompt, choices=choices, sort=False)
        except AttributeError:
            print("Please choose a valid option.")
    return selected


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
                date_not_valid = False
                return date_to_search
        except AttributeError:
            print("No date entered")

def output_sql_rows(query_result, column_names: list, table_headers=None):
    """
    Takes a list of nested dictionaries as input and returns a table with row numbers
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
    return tabulate(output_list, headers="firstrow", tablefmt='grid')


def df_creator(header_array, table_name, query_result):
    """
    Takes an SQL query result and returns a formatted table.
    :param header_array: list of column names to be used for table
    :param table_name: name of table that is printed using CLI_UI module
    :param query_result: SQL result
    :return: table that can be printed
    """
    df = DataFrame(query_result)
    df.columns = header_array
    table = tabulate(df, headers='keys', tablefmt='grid', showindex=False)
    ui.info(ui.red, ui.bold, f"{table_name}")
    return table

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

