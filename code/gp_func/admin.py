from state_manager import StateGenerator
import gp_database as db
import gp_utilities as util
import cli_ui as ui
from pandas import DataFrame
from tabulate import tabulate

states = {
    # admin menu
    "Admin options": ["Manage patient", "Manage GP", "Register new GP", "Approve new patient", "Log out"],
    # Erfan's Options
    # Manage GP menu
    "Choose GP": ["Back"], 
    "Manage GP": ["Edit GP account Information", "Remove GP account", "Deactivate GP account", "Reactivate GP account", "Back"],
    # Edit GP menu
    "Edit GP account information": ["Change GP name", "Change GP registered email address", "Reset GP password", "Back"],
    "Change GP name": ["Back"],
    "Change GP registered email address": ["Back"],
    "reset GP password": ["Back"],
    # Other menus
    "Remove GP account": ["Back"],
    "Deactivate GP account": ["Back"],
    "Reactivate GP account": ["Back"],
}

class Admin():
    def __init__(self, user_id):
        # Create object from userId object from DB
        self.user_id = user_id

        # Get firstname and lastname of admin user 
        self.db = db.Database()
        details_query = "SELECT FIRSTNAME, LASTNAME FROM USERS WHERE USERID = " + str(self.user_id)
        result = self.db.fetch_data(details_query)
        self.firstname, self.lastname = result[0]['firstName'].capitalize(), result[0]['lastName'].capitalize()

        # initialise state machine
        self.state_gen = StateGenerator(state_dict=states, state_object=self)
        self.state_gen.change_state("admin options") 

    def print_welcome(self):
        ui.info_section(ui.blue, 'Welcome to the GP Dashboard')
        print(f"Hi {self.firstname}")

    def handle_state_selection(self, selected):
        if selected == 'Back':
            self.state_gen.call_parent_state()
        else:
            self.state_gen.change_state(selected)

    def admin_options(self):
        self.print_welcome() 
        selected = util.user_select("Please choose one of the options above.", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def log_out(self):
        # TODO
        pass

    # Erfan's methods
    def choose_gp(self):
        pass

    def manage_gp(self):
        # show GPs in system
        gp_acct_query = f"SELECT userID, firstName, lastName, email FROM users WHERE accountType = 'gp'"
        gp_acct_result = self.db.fetch_data(gp_acct_query)
        gp_dataframe_header = ['ID', 'First Name', 'Last Name', 'email']
        gp_dataframe = DataFrame(gp_acct_result)
        gp_dataframe.columns = gp_dataframe_header
        gp_table = tabulate(gp_dataframe, headers='keys', tablefmt='fancy_grid', showindex=False)
        print('\n' + gp_table)



        # # allow admin user to choose desired gp account
        # gp_id_list = GpDataFrame['ID'].tolist()

        # fruits = ["apple", "orange", "banana"]
        # selected_fruit = cli_ui.ask_choice("Choose a fruit", choices=fruits)

        selected = util.user_select("Please choose the ID of the GP you would like to manage.", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def edit_gp_account_information(self):
        selected = util.user_select("Please choose an option?", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def change_gp_name(self):
        selected = util.user_select("Please choose an option?", self.state_gen.get_state_options())
        self.handle_state_selection(selected) 


    
        