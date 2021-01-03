from transitions import State, Machine
from collections import deque


class StateGenerator(Machine):
    """ Take dictionary of state and an object (that will have states applied) to generate state machine with
    functions + transitions. Each state node (dictionary key) will be generated into a State object. Each state
    object will have a function generated with spaces in the state name replaced with underscores. This function can
    then be defined within the model passed to the state machine and will be automatically triggered when that state
    is entered.
    Example:
        dictionary key = "main options"
        function that can be defined within object/model -> main_options
    (this will be auto triggered if "main options" state entered)
    After state is being tracked on the state object/model, you can manage state with the following functions via
    this State Generator object connected to your model:
    - get child nodes of current state node: .get_state_options
    - change state by passing in desired destination state: .change_state(state name: str)
    - change state directly by calling the method: to_<state name with underscores>
    - go to parent state: .call_parent_state
    From an instantiated object you can also manage state with the following additional methods:
    - go back to the previous state: .call_prev_state
    - clear the stack which records state change history: clear_prev_states
        """

    def __init__(self, state_dict, state_object, initial_state='initial'):
        """
        :type state_dict: dict
        :type state_object: object
        :param state_dict: key value dictionary where key = state and value = children of the state
        :param state_object: The object whose state we want to manage.
        :param initial_state: initial state of the object from the state_dict provided.
        """
        self.state_dict = state_dict
        self.state_object = state_object
        super().__init__(state_object, states=self.state_object_list(), initial=initial_state)
        self.__add_auto_transitions()
        self.prev_states = deque()

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
            # add all states as sources to auto transitions 'to_<state>' with destination <state>
            method = "to_" + a_state.lower().strip().replace(" ", "_")
            self.add_transition(method, self.wildcard_all, a_state)

    def change_state(self, state_name):
        """
        Changes an instances state directly with state name as input. Invokes the to_<state> method.
        :param state_name: State to be changed to - key in the state dictionary.
        :return: True on success changed state.
        """
        # from state name find the correct event handler method to trigger state change
        new_state_method = "to_" + state_name.lower().strip().replace(" ", "_")
        try:
            if super()._get_trigger(self.state_object, new_state_method):
                self._store_state(state_name)
                return True
        except AttributeError as err:
            print(str(err) + ": state not found.")

    def _store_state(self, state_trigger_method):
        """Stack implementation to store state methods called
        :param state_trigger_method: to_<state> method name
        """
        self.prev_states.appendleft(state_trigger_method)

    def clear_prev_states(self):
        """ Clear the stack that stores prev states. e.g. if the state goes back to the main state or a high level
        parent node, we may wish to remove what's in the stack to restart. """
        self.prev_states.clear()

    def call_prev_state(self):
        """
        Go back to the previous state of the state machine.
        :return:
        """
        # need to popleft 2, to get prev state. This will then be replaced on stack as when we call change_state method.
        self.prev_states.popleft()
        prev_state = self.prev_states.popleft()
        self.change_state(prev_state)

    def call_parent_state(self, state_name='current_state'):
        """
        Go to state of parent for a given state. if no state specified, defaults to current state.
        :param state_name: defaults to current state of object if not specified.
        :return: True on successful state change.
        """
        # Just in case this is needed, to find the parent state of a child. Although this is not intended to be used
        # frequently. If a child has multiple parents this will only return the first parent found.
        if state_name == 'current_state':
            state_name = self.state_object.state
        for key, value in self.state_dict.items():
            if state_name in value:
                return self.change_state(key)

    @classmethod
    def create_state_machine(cls, state_dict, state_object):
        """
        :param state_dict:
        :param state_object: instantiated class that will now be initialised with state.
        :return: State Machine object
        """
        assert isinstance(state_object, object)
        return cls(state_dict, state_object)