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

