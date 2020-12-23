from pick import pick
import cli_ui as ui


# utility functions for the GP flow


def user_select(title: str, choices: list):
    user_choices = choices
    try:  # if terminal can support, then cursor selection.
        choice, index = pick(user_choices, title)
        return choice
    except Exception:
        selected = ui.ask_choice(title, choices=user_choices, sort=False)
        return selected


def output_sql_rows(query_result, column_index_to_keep, column_name):
    return ui.info_table(data=query_result, headers=['blah1', 'blah2'])
