import logging
import cli_ui as ui
from pick import pick

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
