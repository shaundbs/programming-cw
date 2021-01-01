from .patient_database import Database
from .email_generator import Emails
import re
import datetime as datetime
import getpass # hide password when inputting
import bcrypt
import calendar
from tabulate import tabulate
from termcolor import colored
from pandas import DataFrame
import random
import timedelta
import operator

global ld_nm


class Patient:
    patient_id = 0

    def __init__(self, id):
        self.patient_id = id

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
            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
            email = input('Email:')
            if not re.search(regex, email):
                print("Invalid Email. Please try again.")
            elif email not in email_list:
                email_repetition = False
                break
            else:
                print('This email has been registered. Please try again')

        pWord = getpass.getpass('Password:')
        DoB = input("Date of birth(in YYYY-MM-DD format): ")
        # pWord = pWord.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pWord, salt)
        aType = "patient"
        time_now = datetime.datetime.now()
        date_time = time_now.strftime("%m/%d/%Y %H:%M:%S")
        a = [(fName, lName, email, hashed, aType, date_time, DoB), ]
        db.exec_many(
            "INSERT INTO Users(firstName,lastName,email,password,accountType,signUpDate, date_of_birth) Values (?,?,?,?,?,?,?)",
            a)
        Emails.registration_email(email, fName, lName, "patient")

    def patient_home(self):
        prv = ["Request Appointments", "View Appointments","View Referrals",
               "View Prescription", "Log out"]
        while True:
            option = self.select_options(prv)
            if option == 1:
                self.request_appointment()
            elif option == 2:
                self.view_appointment()
            elif option == 3:
                self.view_referrals()
            elif option == 4:
                self.view_prescription()
            elif option == 5:
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
            option = self.select_options(output)
            if 0 < option < len(output):
                print("No additional information yet.")
            else:
                break

    def date_sort(self, booking_date):
        global ld_nm
        years = [2021, 2022, 2023, 2024, 2025]
        months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        months_list = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

        dates_list = [datetime.datetime.strptime(i, "%m").date().month for i in months_list]

        days_dt = []
        close_dt = []
        years_dt = []
        months_dt = []

        for year in years:
            for i in dates_list:
                days_dt.append(i)

        for year in years:
            for i in months:
                close_dt.append(calendar.monthrange(year, i))

        for date in close_dt:
            years_dt.append(str(date[1]))

        for year in years:
            for i in months:
                months_dt.append(year)

        last_days = [str(n) + "-" + str(o) + "-" + m for m, n, o in zip(years_dt, months_dt, days_dt)]
        last_days_dt = [datetime.datetime.strptime(i, '%Y-%m-%d').date() for i in last_days]

        index_length = range(0, len(last_days_dt))
        for i in index_length:
            while last_days_dt[i - 1] < datetime.datetime.strptime(booking_date, '%Y-%m-%d').date() and i > 0:
                ld_nm = operator.itemgetter(i + 1)(last_days_dt)
                i = i + 1
        return ld_nm

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
            option = self.select_options(apt)
            if option < len(apt):
                # appointmentData is in the format like (1, 'Olivia', 'Cockburn', '12/19/2020 13:00:00', '12/19/2020 14:00:00', 0, 0).
                appointmentData = self.appointmentList[option - 1]
                if (appointmentData[-2] + appointmentData[-1]) == 0:
                    print("\nThis appointment is not approved yet.")
                    apt = ["Cancel this appointment.", "Back."]
                    option = self.select_options(apt)
                    if option == 1:
                        self.cancel_appointment(appointmentData[0])
                    elif option == 2:
                        break

                elif appointmentData[-2] == 0:
                    print("\nThis appointment is rejected.\n")
                    apt = ["Reschedule this appointment.",
                           "Cancel this appointment.", "Back."]
                    option = self.select_options(apt)
                    if option == 1:
                        self.reschedule_appointment(appointmentData[0])
                    elif option == 2:
                        self.cancel_appointment(appointmentData[0])

                elif appointmentData[-1] == 0:
                    print("\nThis appointment is confirmed.\n")
                    apt = ["Reschedule this appointment.",
                           "Cancel this appointment.", "Back."]
                    option = self.select_options(apt)
                    if option == 1:
                        self.reschedule_appointment(appointmentData[0])
                    elif option == 2:
                        self.cancel_appointment(appointmentData[0])
            else:
                break

    def request_appointment(self):
        while True:
            menu_choice = self.select_options(
                ["Book an appointment this month.", "Book an appointment next month.", "Back."])

            if menu_choice in [1, 2]:
                if menu_choice == 1:
                    date = datetime.datetime.today()
                elif menu_choice == 2:
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
                select_date = input(
                    "Please enter a valid date in YYYY-MM-DD format between now and the close of the month(enter 'b' to exit): ")
                # print(self.date_sort("2021-10-24"))
                if select_date == 'b':
                    break
                try:
                    fm_selected = datetime.datetime.strptime(
                        select_date, '%Y-%m-%d').date()
                    if datetime.datetime.now().date() < fm_selected <= datetime.datetime.now().date() + \
                            datetime.timedelta(1 * 365 / 12):
                        print('The date {} is valid. Listing appointments... \n'.format(
                            select_date))
                        self.select_slots(select_date)
                    else:
                        print(
                            "We are unable to book appointments in the past or too far in the future.\nPlease enter a valid date between today and the close of next month")
                except ValueError:
                    print("Your input is not valid.")
            else:
                break

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
                                     " inform your assigned GP... \n"
                                     "or hit enter if you do not want to disclose now: \n ")
                    key = session[booked_slot][:2]
                    slot = result[key][0][1]
                    gp = result[key][0][0]
                    gp_name = self.db.gp_name(gp)
                    a = (self.patient_id, slot, gp, symptoms)
                    # Insert request into database.
                    print("Do you confirm that you want to book this appointment?")
                    option = self.select_options(["Yes", "No"])
                    if option == 1:
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
            a = self.select_options(["Yes", "No"])
            if a == 1:
                appointmentNo = int(appointmentNo)
                Database().delete_appointment(appointmentNo)
                print("You have successfully cancelled this appointment")
            break

    def view_prescription(self):
        print("Patient id: " + str(self.patient_id) +
              "want to view prescription\n")
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

    def select_options(self, options):
        # TODO: Move to utilities.
        selected = 0
        while selected < 1 or selected > len(options):
            try:
                # Print privileges.
                num = 1
                for i in options:
                    print(str(num) + ". " + i)
                    num += 1
                selected = int(input('Please choose an option: '))
            except ValueError:
                # Handle exceptions.
                print("No valid integer! Please try again ...\n")
        return selected


if __name__ == "__main__":
    Patient(4).patient_home()
