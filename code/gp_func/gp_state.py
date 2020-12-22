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


class StateGenerator(Machine):
    """ Take dictionary of state and generate state functions + transitions.
     Each state node will be generated into a State object.
     Each state object will have on_enter function generate with spaces replaced with underscores.
     This function can then be defined within the model passed to the state machine."""

    def __init__(self, state_dict, state_object, initial_state='initial'):
        """
        :param state_dict: key value dictionary where key = state and value = children of the state
        :param state_object: The object whose state we want to manage.
        :param initial_state: inital state of the object from the state_dict provided.
        """
        self.state_dict = state_dict
        self.state_object = state_object
        super().__init__(state_object, states=self.state_object_list(), initial=initial_state)
        self.__add_auto_transitions()

    def state_object_list(self):
        """ for each dictionary key generate list of objects of the state class with an on_enter function. [ State(
        name='main options', on_enter=['main_options']), etc, etc ] """
        states_list = []
        for key in self.state_dict:
            try:
                func = key.lower().replace(" ", "_").strip()
                state_info = State(name=key, on_enter=[func])
                states_list.append(state_info)
            except AttributeError:
                print("Invalid state. Please only use strings for states.")
        return states_list

    def get_state_options(self):
        """ get the children of a state i.e. options for that node. Empty list if no options. """
        try:
            return self.state_dict[self.state_object.state]
        except KeyError as err:
            print("Oops, state " + str(err) + " not defined yet.")

    #         TODO: add logging for errors like these.

    def __add_auto_transitions(self):
        """
        Add the capability for all states to have a transition to_<state> to initialise the state with and spaces in
        <state> being replaced by underscores.
        """
        for a_state in self.states.keys():
            # add all states as sources to auto transitions 'to_<state>' with dest <state>
            method = "to_" + a_state.lower().strip().replace(" ", "_")
            self.add_transition(method, self.wildcard_all, a_state)

    # def get_state_transition

    @classmethod
    def create_state_machine(cls, state_dict, state_object):
        """
        :param state_dict:
        :param state_object: instantiated class that will now be initialised with state.
        :return: State Machine object
        """
        assert isinstance(state_object, object)
        return cls(state_dict, state_object)


class MyClass:
    def main_options(self):
        print("hello")

    def manage_calendar(self):
        print("calendar entered!!!")

    # def on_enter_mainoptions(self):
    #     print("in state MAIN OPTIONS!!!")


# test_class = MyClass()
#
# test1 = StateGenerator(state_dict=states, state_object=test_class)
#
# test.set_state("main options")
#  # why on enter is it not executing the function in MYClass - ok works only when the object has been instantiated!!
#
# print(test_class.state)
# # print(test_class.main_options())
#
# print(test.state_object_list())
#
# print(test.get_state_options())
#
# test.set_state("manage calendar")
#
# print(test_class.state)

# test1 = Machine(test_class, states=[State(name="mainoptions",on_enter="main_options"), "manage calendar"])

# test1.on_enter_mainoptions('main_options')

# print(test_class.state)
#
# # print(test1.set_state("main options"))
#
# print(test_class.state)
#
# test_class.to_main_options()

# print(test1.events)
#
# test1._add_auto_transitions()
#
# print(test1.events)


# Generate state machine.
# Should be able to:
# keep track of previous state via linked list?
# take in dict, create transitions for each state via graph.
