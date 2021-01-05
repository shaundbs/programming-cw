import cli_ui as ui
import re


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


