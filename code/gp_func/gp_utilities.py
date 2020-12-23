from pick import pick
import cli_ui as ui


# utility functions for the GP flow


def user_select(title: str, choices: list, back=False):

    if back: # add a back button
        choices.append("back")
    try:  # if terminal can support, then cursor selection.
        choice, index = pick(choices, title)
        return choice
    except Exception:
        selected = ui.ask_choice(title, choices=choices, sort=False)
        return selected
