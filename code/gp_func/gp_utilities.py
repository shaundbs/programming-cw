from pick import pick
import cli_ui as ui
from terminaltables import AsciiTable as Table
import gp_database as db


# utility functions for the GP flow


def user_select(title: str, choices: list):
    # try:  # if terminal can support, then cursor selection.
    #     choice, index = pick(choices, title)
    #     return choice
    # except Exception:
    selected = ui.ask_choice(title, choices=choices, sort=False)
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
        for header in column_names[1:]:  # skip initial header i.e. row header
            record.append((values[header]))
        output_list.append(record)
    return Table(output_list).table


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

