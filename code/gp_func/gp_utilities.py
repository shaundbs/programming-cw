from pick import pick
import cli_ui as ui
from terminaltables import AsciiTable as table

# utility functions for the GP flow


def user_select(title: str, choices: list):
    user_choices = choices
    try:  # if terminal can support, then cursor selection.
        choice, index = pick(user_choices, title)
        return choice
    except Exception:
        selected = ui.ask_choice(title, choices=user_choices, sort=False)
        return selected


def output_sql_rows(query_result, column_names: list, table_headers=[]):
    output_list = []
    if table_headers:
        table_headers.insert(0, "row")
        output_headers = table_headers
    else:
        column_names.insert(0, "row")
        output_headers = column_names
    output_list.append(output_headers)
    for row, values in enumerate(query_result, start=1):
        record = [row]
        for header in column_names[1:]: # skip initial header i.e. row header
            record.append((values[header]))
        output_list.append(record)
    return table(output_list).table

