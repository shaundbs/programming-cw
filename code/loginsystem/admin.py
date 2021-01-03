from state_gen import StateGenerator
import gp_database as db
import gp_utilities as util
import cli_ui as ui
from pandas import DataFrame
from tabulate import tabulate
from registerGP import registerGP, confirmation
from confirmPatient import confirmPatient, validate, clear
from time import sleep


states = {
    # admin menu
    "Admin options": ["Manage patient", "Manage GP", "Register new GP", "Approve new patients", "Log out"],
    "Return to menu": ["Manage patient", "Manage GP", "Register new GP", "Approve new patients", "Log out"],

    # Register GP
    "Register new GP": ["Confirm details", "Back"],
    "Confirm details": ["Register another GP", "Return to menu"],
    "Register another GP": ["Confirm details", "Return to menu"],

    # Confirm Patient
    "Approve new patients": ["Continue validation", "Back"],
    "Continue validation": ["Validate more entries", "Return to menu"],
    "Validate more entries": ["Continue validation", "Return to menu"],



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
        ui.info_section(ui.blue, 'Welcome to the Admin Dashboard')
        print(f"Hi {self.firstname}")

    def handle_state_selection(self, selected):
        if selected == 'Back':
            self.state_gen.call_parent_state()
        else:
            self.state_gen.change_state(selected)

    def admin_options(self):
        clear()
        self.print_welcome()
        ver = False
        while ver == False:

            selected = util.user_select("Please choose one of the options below.", self.state_gen.get_state_options())
            self.handle_state_selection(selected)

            if selected is None:
                print("Choose an option!")
            else:
                ver = True


    def register_new_gp(self):
        registerGP()
        selected = util.user_select("Please choose one of the options below.", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def confirm_details(self):
        confirmation()
        selected = util.user_select("Please choose one of the options below.", self.state_gen.get_state_options())
        self.handle_state_selection(selected)




    def register_another_gp(self):
        self.register_new_gp()

    def approve_new_patients(self):
        try:
            confirmPatient()
            selected = util.user_select("Please choose one of the options below.", self.state_gen.get_state_options())
            self.handle_state_selection(selected)
        except:
            print("\nNo patients currently require validation!\nRedirecting...")
            sleep(3)
            self.to_admin_options()



    def continue_validation(self):
        validate()
        selected = util.user_select("Please choose one of the options below.", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def validate_more_entries(self):
        self.approve_new_patients()


    def return_to_menu(self):
        self.admin_options()

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



        selected = util.user_select("Please choose the ID of the GP you would like to manage.", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def edit_gp_account_information(self):
        selected = util.user_select("Please choose an option?", self.state_gen.get_state_options())
        self.handle_state_selection(selected)

    def change_gp_name(self):
        selected = util.user_select("Please choose an option?", self.state_gen.get_state_options())
        self.handle_state_selection(selected)