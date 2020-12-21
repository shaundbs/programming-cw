# GP state management module. Specify states and their characteristics.

"""
We need to have a graph/tree of states.
At each state the options presented top the user will be the children of the current state node.
The back option will be to the parent node.

Given a graph of major states we need to be able to:
show child nodes of current state + parent node - function
show parent node of current state (back button) - function

each state also needs it's own function to control flow etc

Flow:
app has state
state has options
from option selected we move to that state. (to_{state} method)
each state has it's own function to control flow, auto triggered on_enter of that state. auto function name = trim(state name) replace ' ' with _
"""

from transitions import State, Machine

# state dictionary to map out possible routes from each state/node

states = {
    "main options": ["manage calendar", "confirm appointments", "view appointments"],
    # Calendar / holiday
    "manage calendar": ["view calendar", "schedule time off"],
    "view calendar": [],
    "schedule time off": [],
    # confirm appts
    "confirm appointments": [],
    # view appts
    "view appointments": ["show appointments from another day", "show appointment details"],
    "show appointments from another day": [],
    "show appointment details": ["write prescriptions"]
}


class StateGenerator:
    """ Take dictionary of state and generate state functions + transitions.
     Each state node will be generated into a State object"""

    def __init__(self, state_dict):
        self.state_dict = state_dict

    def state_object_list(self):
        #generate list of object of the State class with an on_enter functions. [ State(name='solid', on_enter=['solid']), etc, etc ]





# Generate state machine.
# Should be able to:
# keep track of previous state via linked list?
# take in dict, create transitions for each state via graph.

