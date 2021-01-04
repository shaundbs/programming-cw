from patient_database import Database
from email_generator import Emails
import re
import datetime as datetime
import getpass  # hide password when inputting
import bcrypt
import calendar
from tabulate import tabulate
from termcolor import colored
from pandas import DataFrame
import random
import operator
import cli_ui as ui
import date_generator
from dateutil.relativedelta import relativedelta
# import gp_utilities
import timedelta as td


class Patient:
    patient_id = 0

    def __init__(self, id):
        self.patient_id = id
        self.db = Database()
        self.tobecanceled = -1
        self.testing = ""

    @classmethod
    def register(cls):
        # Register. User input.
        # TODO: data validation.
        fName = input('First Name:')
        lName = input('Last Name:')
        db = Database()

        email_repetition = True
        email_list = Database().patient_email_list()

        while email_repetition:
            regex = '^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$'
            email = input('Email:')
            if not re.search(regex, email):
                print("Invalid Email. Please try again.")
            elif email not in email_list:
                email_repetition = False
                break
            else:
                print('This email has been registered. Please try again')

        pWord = input('Password: ')
        DoB = input("Date of birth(in YYYY-MM-DD format): ")
        pWord = pWord.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pWord, salt)
        aType = "patient"
        time_now = datetime.datetime.now()
        date_time = time_now.strftime("%m-%d-%Y %H:%M:%S")
        a = [(fName, lName, email, hashed, aType, date_time, DoB), ]
        db.exec_many(
            "INSERT INTO Users(firstName,lastName,email,password,accountType,signUpDate, date_of_birth) Values (?,?,?,?,?,?,?)",
            a)
        Emails.registration_email(email, fName, lName, "patient")


    def patient_home(self):
            prv = ["Request Appointment", "View Appointments", "View Referrals","View Prescriptions", "Log out"]

            while True:
                option = ui.ask_choice("Choose an option:", choices=prv,sort=False)
                if option == prv[0]:
                    self.request_appointment()
                elif option == prv[1]:
                    self.view_appointment()
                elif option == prv[2]:
                    self.view_referrals()
                elif option == prv[3]:
                    self.view_prescription()
                elif option == prv[4]:
                    break

    def view_referrals(self):
        """
        docstring
        """
        while True:
            # Fetch referrals from db.
            self.db.exec_one("SELECT a.referred_specialist_id, s.firstName, s.lastName, s.hospital, d.name FROM Appointment a, Specialists s, Department d WHERE  s.department_id = d.department_id AND a.referred_specialist_id = s.specialist_id AND patient_id = ? AND a.referred_specialist_id IS NOT NULL", (self.patient_id,))
            result = self.db.c.fetchall()
            self.referralsList = []
            for i in result:
                self.referralsList.append(list(i))
            output = []
            for i in self.referralsList:
                output.append("Your are referred to our specialist Dr " + str(i[1]) + " " + str(
                    i[2]) + " at Department " + str(i[4]) + " of Hopsital " + str(i[3]) + ".")
            output.append("Back.")
            option = ui.ask_choice("Choose a referral:", choices=output, sort=False)
            if option != "Back.":
                print("No additional information yet.")
            else:
                break

    def view_appointment(self):
        while True:
            # Fetch appointments from db.
            self.db.exec_one(
                "SELECT a.appointment_Id, u.firstName, u.lastName, s.startTime, s.endTime, a.is_confirmed, a.is_rejected FROM Appointment a, Slots s, Users u WHERE a.gp_id = u.userId AND a.slot_id = s.slot_id And a.patient_id = ? ORDER BY startTime",
                (self.patient_id,))
            self.appointmentList = []
            result = self.db.c.fetchall()
            for i in result:
                self.appointmentList.append(i)

            # Print appointments and options.
            print("")
            apt = []
            for i in self.appointmentList:
                if i[-2] + i[-1] == 0:
                    status = "not yet confirmed."
                elif i[-2] == 1:
                    status = "confirmed."
                else:
                    status = "rejected."
                apt.append("Your appointment with Dr " +
                           str(i[1]) + " " + str(i[2]) + " at " + str(i[3][:10]) + " is " + status)
            apt.append("Back")
            # Redirects to appointment management.
            option = ui.ask_choice("Choose an appointment", choices=apt, sort=False)
            option = list.index(apt, option)
            if option < len(apt) - 1:
                # appointmentData is in the format like (1, 'Olivia', 'Cockburn', '12/19/2020 13:00:00', '12/19/2020 14:00:00', 0, 0).
                appointmentData = self.appointmentList[option]
                if (appointmentData[-2] + appointmentData[-1]) == 0:
                    print("\nThis appointment is not approved yet.")
                    apt = ["Cancel this appointment.", "Back."]
                    option = ui.ask_choice("Choose an option", choices=apt, sort=False)
                    option = list.index(apt, option)
                    if option == 0:
                        self.cancel_appointment(appointmentData[0])
                        continue

                elif appointmentData[-2] == 0:
                    print("\nThis appointment is rejected.\n")

                elif appointmentData[-1] == 0:
                    print("\nThis appointment is confirmed.\n")
                apt = ["Reschedule this appointment.",
                       "Cancel this appointment.", "Back."]
                option = ui.ask_choice("Choose an option", choices=apt, sort=False)
                option = list.index(apt, option)
                if option == 0:
                    self.reschedule_appointment(appointmentData[0])
                elif option == 1:
                    self.cancel_appointment(appointmentData[0])
            else:
                break

    def request_appointment(self):
        while True:
            apt = ["Book an appointment this month.", "Book an appointment next month.", "Back."]
            menu_choice = ui.ask_choice("Choose an appointment", choices=apt, sort=False)
            menu_choice = list.index(apt, menu_choice)
            if menu_choice in [0, 1]:
                if menu_choice == 0:
                    date = datetime.datetime.today()
                elif menu_choice == 1:
                    date = datetime.datetime.today() + datetime.timedelta(1 * 365 / 12)
                year_now = datetime.datetime.date(date).strftime("%Y")
                month_now = datetime.datetime.date(date).strftime("%m")
                day_now = datetime.datetime.date(date).strftime("%d")
                c = calendar.TextCalendar(calendar.MONDAY)
                year_input, month_input, day_input = int(
                    year_now), int(month_now), int(day_now)
                calendar_month = c.formatmonth(
                    year_input, month_input, day_input, 0)
                print(calendar_month)
                apt = ["Enter booking date",
                       "Back"]
                date_booker = ui.ask_choice("Choose an option", choices=apt, sort=False)
                date_booker = list.index(apt, date_booker)
                if date_booker in [0, 1]:
                    while True:
                        if date_booker == 0:
                            select_date = input(
                                "Please enter a valid date in YYYY-MM-DD format between now and the close of the month: "
                              )
                            dn = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
                            last_booking_date = date_generator.date_sort(dn)
                            try:
                                year, month, day = select_date.split('-')
                                isValidDate = True
                                datetime.datetime(int(year), int(month), int(day))
                            except ValueError:
                                isValidDate = False
                            if (isValidDate):
                                self.limit_appointment_bookings(select_date)
                                if self.limit_appointment_bookings(select_date) == 0:
                                    fm_selected = datetime.datetime.strptime(
                                        select_date, '%Y-%m-%d').date()
                                    if datetime.datetime.now().date() < fm_selected <= last_booking_date:
                                        print('The date {} is valid. Listing appointments... \n'.format(
                                            select_date))
                                        self.select_slots(select_date)
                                    elif fm_selected < datetime.datetime.now().date():
                                        print("Sorry, we are unable to book appointments for dates in the past")
                                    elif fm_selected == datetime.datetime.now().date():
                                        print("Sorry, we are unable to book appointments on the day as we must give our GP's prior notice")
                                    else:
                                        print(
                                            "Sorry, we are unable to book appointments too far into the future.\n"
                                            "Please enter a valid date between today and the close of next month:", last_booking_date)
                                elif self.limit_appointment_bookings(select_date) > 0:
                                    print(
                                        "Sorry you already have an appointment booked for this week. \nTo ensure that our GPs are able to see "
                                        "as many patients as possible and there is fair assignment in place, "
                                        "please select an alternative week where you"
                                        " do not currently have an appointment booked.")
                                    continue
                            elif not(isValidDate):
                                print("Sorry this value is not accepted")
                                opts = ["Try again",
                                       "Back to booking options menu"]
                                navigate = ui.ask_choice("Choose an option", choices=opts, sort=False)
                                navigate = list.index(opts, navigate)
                                if navigate in [0, 1]:
                                    if navigate == 1:
                                        break
                                    elif navigate == 2:
                                        break
                            else:
                                print("This input will not be accepted im afraid - Please re-enter in YYYY-MM-DD format")
                        elif date_booker == 1:
                            break
            elif menu_choice == 2:
                break
            else:
                print("System Failure: please restart")

    def limit_appointment_bookings(self, select_date):
        day = select_date
        dt = datetime.datetime.strptime(day, '%Y-%m-%d')
        start = dt - td.Timedelta(days=dt.weekday())
        end = start + td.Timedelta(days=4)
        self.db.exec("""SELECT count(a.appointment_id) FROM Appointment AS A
                            LEFT JOIN Slots AS S
                            ON s.slot_id = a.slot_id
                            WHERE a.patient_id = '""" + str(self.patient_id) + """' AND
                            s.startTime BETWEEN '""" + str(start) + """' AND '""" + str(end) + """'""")
        result = self.db.c.fetchall()
        x = result[0]
        weekly_appointment_count = x[0]
        return weekly_appointment_count



    def reschedule_appointment(self, appointmentNo):
        self.tobecanceled = appointmentNo
        self.request_appointment()

    def available_session(self, select_date):
        self.db.exec_one("""SELECT substr(s.startTime, 12, 2), s.slot_id, u.firstName, u.lastName, u.userId as gp_id, row_number() OVER (PARTITION by s.slot_id order by random()) as rand_order
                    FROM SLOTS S
                    CROSS JOIN Users U
                    LEFT JOIN APPOINTMENT A
                    ON S.slot_id= A.slot_id
                    AND A.gp_id = U.userId
                    AND ((A.IS_CONFIRMED =0 AND A.IS_REJECTED=0) OR (A.is_confirmed=1))
                    LEFT JOIN gp_time_off gpto
                    ON datetime(S.startTime) >= datetime(GPTO.startTime) AND
                    datetime(s.startTime) < datetime(GPTO.endTime)
                    AND GPTO.gp_id = U.userId
                    WHERE U.accountType='gp'
                    and
                    u.is_active = 1
                    AND DATE(S.startTime) = DATE(?)
                    AND A.GP_ID IS NULL
                    AND GPTO.GP_ID IS NULL""", (select_date,))
        result = self.db.c.fetchall()
        rows = []
        for i in result:
            rows.append(list(i))
        # rows: list of available options.
        # awailable session: ['09': [1,2], ...] (list of sessions(gp at same slot combined into one row)).
        available_session = {}
        for i in rows:
            if i[0] in available_session:
                available_session[i[0]].append([i[4], i[1]])
            else:
                available_session[i[0]] = [[i[4], i[1]]]

        # Prompt user to select slots.
        print("Please select an appointment time:")
        sessions = ["09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00",
                    "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00"]
        num = 0
        result_session = []
        for i in sessions:
            if i[:2] in list(available_session.keys()):
                result_session.append(i)
                num += 1
        # Display sessions.
        index_1 = ["Available Slots"]
        df1 = DataFrame(result_session)
        df1.columns = index_1
        self.display_opening_hours(select_date)
        print(colored('Available slots on the ' + select_date + ' ', 'green',
                      attrs=['bold']))
        print(tabulate(df1, headers='keys',
                       tablefmt='fancy_grid', showindex=True))
        print(str(num) + ". Back")
        return [result_session, available_session]

    def select_slots(self, select_date):
        while True:
            # self.display_opening_hours(select_date)
            output = self.available_session(select_date)
            result = output[1]
            session = output[0]
            try:
                booked_slot = int(input("Enter your option : "))

                if booked_slot == len(result):
                    break
                elif booked_slot in range(8):
                    # Assign GP6 to this appointment temporarily.
                    # selected_session = available_session[booked_slot - 1][:2]
                    # ask the patient to input any symptoms they may have or default value is 'none'
                    symptoms = input("Please list any symptoms or concerns you may have so that we may"
                                     " inform your assigned GP...\n"
                                     "or hit enter if you do not want to disclose now: \n ")
                    key = session[booked_slot][:2]
                    slot = result[key][0][1]
                    gp = result[key][0][0]
                    gp_name = self.db.gp_name(gp)
                    a = (self.patient_id, slot, gp, symptoms)
                    # Insert request into database.
                    print("Do you confirm that you want to book this appointment?")

                    option = ui.ask_choice("Choose an option", choices=["Yes", "No"], sort=False)
                    option = list.index(["Yes", "No"], option)
                    if option == 0:
                        if self.tobecanceled > 0:
                            self.db.reschedule(a, self.tobecanceled)
                            self.tobecanceled = -1
                            print(
                                "SUCCESS - \nYou have successfully reshceduled an appointments with Dr "+str(gp_name[0]) + " " + str(gp_name[1]) + ", You will be alerted once your appointment is confirmed")
                        else:
                            self.db.exec_one(
                                "INSERT INTO Appointment(patient_id,slot_id,gp_id,reason) Values (?,?,?,?)", a)
                            print(
                                "SUCCESS - \nYou have successfully requested an appointments with Dr "+str(gp_name[0]) + " " + str(gp_name[1]) + ", You will be alerted once your appointment is confirmed")
                    break
            except ValueError:
                print("Please select a valid option.")

    def cancel_appointment(self, appointmentNo):
        while True:
            print("Do you confirm that you want to cancel this appointment?")
            a = ui.ask_choice("Choose an option", choices=["Yes", "No"], sort=False)
            a = list.index(["Yes", "No"], a)
            if a == 0:
                appointmentNo = int(appointmentNo)
                Database().delete_appointment(appointmentNo)
                print("You have successfully cancelled this appointment")
            break

    def view_prescription(self):
        # gp_utilities.print_appointment_summary(self.patient_id)
        return

    def display_opening_hours(self, selected):
        # get datetime object of the first and last appointments on that day = Opening hours
        fm_date = datetime.datetime.strptime(
            selected, '%Y-%m-%d').date()
        self.db.exec_one("SELECT min(startTime), max(endTime) FROM SLOTS "
                         "WHERE startTime like (?)", ("%" + str(fm_date) + "%",))
        index_2 = ["Opening Time", "Closing time"]
        output = self.db.c.fetchall()

        # create table with opening hour info
        df2 = DataFrame(output)
        df2.columns = index_2
        print(colored('Opening hours: ' +
                      selected + ' ', 'green', attrs=['bold']))
        print(tabulate(df2, headers='keys',
                       tablefmt='fancy_grid', showindex=False))
        return output[0]


    # def select_options(self, options):
    #     # TODO: Move to utilities.
    #     selected = 0
    #     while selected < 1 or selected > len(options):
    #         try:
    #             # Print privileges.
    #             num = 1
    #             for i in options:
    #                 print(str(num) + ". " + i)
    #                 num += 1
    #             selected = int(input('Please choose an option: '))
    #         except ValueError:
    #             # Handle exceptions.
    #             print("No valid integer! Please try again ...\n")
    #     return selected


if __name__ == "__main__":
    Patient(4).patient_home()
