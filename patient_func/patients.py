from .patient_database import Database
from .patient_email_generator import Emails
from . import date_generator
import re
import datetime as datetime
import bcrypt
import calendar
from tabulate import tabulate
from termcolor import colored
from pandas import DataFrame
import random
import cli_ui as ui
from datetime import timedelta as td
import csv
import os
import pandas as pd
from dateutil.relativedelta import relativedelta
import threading
from . import patient_utilities as util
import time
import sys

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
        while True:
            fName = input('First Name:')
            if fName.isalpha():
                fName = fName.capitalize()
                break
            else:
                print("Please only include letters.")
        while True:
            lName = input('Last Name:')
            if lName.isalpha():
                lName = lName.capitalize()
                break
            else:
                print("Please only include letters.")

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
        while True:
            pWord = ui.ask_password('Password:')
            if len(pWord) < 8:
                print("Please note that the minimum length of password is 8.")
            else:
                confirmpwd = ui.ask_password('Confirm your password:')
                if pWord == confirmpwd:
                    break
                else:
                    print("Sorry, you created different passwords. Please try again.\n")
        while True:
            DoB = input("Date of birth(in YYYY-MM-DD format): ")
            try:
                # check if the date is in YYYY-MM-DD format
                year, month, day = DoB.split('-')
                isValidDate = True
                datetime.datetime(int(year), int(month), int(day))
            except ValueError:
                isValidDate = False
            if isValidDate:
                fm_selected = datetime.datetime.strptime(
                    DoB, '%Y-%m-%d').date()
                if fm_selected < datetime.datetime.now().date() - relativedelta(years=120):
                    print("Sorry the date of birth entered is too far into the past - please try again")
                    continue
                elif fm_selected > datetime.datetime.now().date():
                    print("It is not possible for your DoB to be set in the future - please try again")
                    continue
                elif fm_selected > datetime.datetime.now().date() - datetime.timedelta(16 * 365):
                    print(
                        "Sorry, you must be at least 16 years of age to register for this e-health management service")
                    continue
                elif fm_selected < datetime.datetime.now().date():
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
                    util.clear()
                    print('You have successfully requested an account. Please wait for confirmation from us:)')
                    task = threading.Thread(target=Emails.registration_email, args=(email, fName, lName, "patient"),
                                            daemon=True)
                    task.start()
                    break
            elif not isValidDate:
                print("Sorry this input is not accepted. Please re-enter your DoB in YYYY-MM-DD format")
                continue

    def print_welcome(self):
        self.db.exec("""SELECT firstName, lastName FROM Users WHERE userId = '""" + str(self.patient_id) + """'""")
        output = self.db.c.fetchall()
        y = output[0]
        fName = y[0]
        lName = y[1]
        ui.info_section(ui.blue, '\nWelcome to the Patient Dashboard')
        print("Hi, " + fName + " " + lName + "\n")

    def patient_home(self):
        self.print_welcome()
        prv = ["Request appointment", "View appointments", "View referrals", "View prescriptions", "Help?", "Log out"]
        # if user has an appointment to receive vaccine
        if self.covid_appt_count() >= 1:
            # have they received it yet or not - if so clear notification
            self.dismiss_covid_notification()
        else:
            # if user has no appointments - find out if they are high risk based on age and qualify for vaccine
            if self.high_risk_top_waitinglist_notification():
                print(" ")
            # if age < 60 == low-risk patient
            elif self.low_risk_notification():
                print(" ")
            # if high-risk but registered with us >30 days
            elif not self.high_risk_top_waitinglist_notification():
                print(colored('*COVID-19 status notification*', 'red',
                              attrs=['bold']))
                print("-- You have been identified as a high risk patient to COVID-19 and have been placed on our "
                      "waiting list.\n- This classification has been made based on your age making you more "
                      "susceptible to the virus.\n- You will be invited to receive a vaccination with us "
                      "in due course.\n")

        while True:
            option = ui.ask_choice("Choose an option:", choices=prv, sort=False)
            util.clear()
            if option == prv[0]:
                self.request_appointment()
            elif option == prv[1]:
                self.view_appointment()
            elif option == prv[2]:
                self.view_referrals()
            elif option == prv[3]:
                self.view_prescription()
            elif option == prv[4]:
                print(colored('*Help*', 'yellow',
                              attrs=['bold']))
                print("Please select an feature that you need assistance with:\n")
                while True:
                    try:
                        incrementer = 1
                        help_options = prv[:4]
                        help_options.append("Back")
                        for i in help_options:
                            print(str(incrementer) + " " + str(i))
                            incrementer += 1
                        print(" ")
                        ask_for_help = int(input("Which feature would you like help with?: "))
                        if ask_for_help in range(6):
                            if ask_for_help == 1:
                                util.clear()
                                print(" ")
                                util.loader('Loading')
                                print("\n")
                                util.clear()
                                print(colored('*Request Appointment Help Screen*', 'yellow',
                                              attrs=['bold']))
                                print("--This section offers help and guidance with regards to patients requesting "
                                      "appointments\n\nConditions for requesting appointments:\n\n1.You can only request "
                                      "appointments for "
                                      "weekdays (weekends excluded)\n2.You can only request up until the last working day"
                                      " of the following month (e.g if date is 2021-01-07 the patient can only request up "
                                      "until 2021-02-26)\n3.You cannot request appointments for a date in the past or on the "
                                      "date of login\n4.You cannot request an appointment for a week where you already"
                                      " have an appointment confirmed by one of our GPs\n\n-Once you have requested a "
                                      "valid date the time slot for the date where we have GP's available will be"
                                      " presented to the patient\n-Then the patient can select a timeslot that suits"
                                      " their own availability and proceed to enter symptoms/concerns if they wish to "
                                      "do so before confirming the appointment request\n ")
                                break
                            elif ask_for_help == 2:
                                util.clear()
                                print(" ")
                                util.loader('Loading')
                                print("\n")
                                util.clear()
                                print(colored('*View Appointments Help Screen*', 'yellow',
                                              attrs=['bold']))
                                print("--This section offers help and guidance with regards to patients viewing "
                                      "appointments\n\n-In the viewing appointments tab patients can see information"
                                      " regarding upcoming appointments, these appointments are classified as either"
                                      " 'requested' or 'confirmed'\n-Requested appointments can be cancelled and this "
                                      "will remove the appointment from the patient's view\n-Confirmed appointments "
                                      "offer more features with the user then having the ability to select any"
                                      " appointment that they would like to view in greater detail and "
                                      "view the appointment date, time slot, and assigned GP\n\n")
                                break
                            elif ask_for_help == 3:
                                util.clear()
                                print(" ")
                                util.loader('Loading')
                                print("\n")
                                util.clear()
                                print(colored('*View Referrals Help Screen*', 'yellow',
                                              attrs=['bold']))
                                print("--This section offers help and guidance with regards to patients viewing "
                                      "referrals\n\n-This is a simple feature that displays information of referrals"
                                      " to our external medical professionals\n-This information includes"
                                      " the specialist's name, the department they work in and the hospital or medical"
                                      " practice where they work\n-Patients have the option to contact the specialists "
                                      "and consider booking a consultation for further examination following an "
                                      "appointment with one of our GPs\n\n")
                                break
                            elif ask_for_help == 4:
                                util.clear()
                                print(" ")
                                util.loader('Loading')
                                print("\n")
                                util.clear()
                                print(colored('*View Prescriptions Help Screen*', 'yellow',
                                              attrs=['bold']))
                                print("--This section offers help and guidance with regards to patients viewing "
                                      "prescriptions\n\n-If the patient navigates to this tab, a table is printed "
                                      "containing information about their past prescriptions.\n-The patient then has"
                                      " option to save and print the prescription summary as either a .csv or .txt file"
                                      "\n-nb. These files are saved locally in the repo in the directory '"
                                      "../downloaded_data/Prescriptions'\n\n")
                                break
                            elif ask_for_help == 5:
                                util.clear()
                                self.print_welcome()
                                break
                        else:
                            print("Integer out of range\n")
                            continue
                    except ValueError:
                        print("Please enter numerical values only\n")
                        continue
            elif option == prv[5]:
                util.clear()
                print(" ")
                util.loader("Logging out")
                print(" ")
                sys.exit()


    def view_referrals(self):
        """
        docstring
        """
        util.clear()
        while True:
            # Fetch referrals from db.
            self.db.exec_one(
                "SELECT a.referred_specialist_id, s.firstName, s.lastName, s.hospital, d.name FROM Appointment a, Specialists s, Department d WHERE  s.department_id = d.department_id AND a.referred_specialist_id = s.specialist_id AND patient_id = ? AND a.referred_specialist_id IS NOT NULL",
                (self.patient_id,))
            result = self.db.c.fetchall()
            self.referralsList = []
            for i in result:
                self.referralsList.append(list(i))
            output = []
            print(" ")
            util.loader('Loading')
            print("\n")
            util.clear()
            for i in self.referralsList:
                output.append("You are referred to our specialist Dr. " + str(i[1]) + " " + str(
                    i[2]) + " at Department " + str(i[4]) + " of Hopsital " + str(i[3]) + ".")
            if len(output) == 0:
                print("Sorry, you have no referrals at the moment.\n")
                break
            output.append("Back.")
            option = ui.ask_choice("Choose a referral:", choices=output, sort=False)
            util.clear()
            if option != "Back.":
                print("No additional information yet.")
            else:
                self.print_welcome()
                break

    def view_appointment(self):
        while True:
            # Fetch appointments from db.
            self.db.exec_one(
                "SELECT a.appointment_Id, u.firstName, u.lastName, s.startTime, s.endTime, a.is_confirmed, a.is_rejected,a.is_completed FROM Appointment a, Slots s, Users u WHERE a.gp_id = u.userId AND a.slot_id = s.slot_id And a.patient_id = ? ORDER BY startTime",
                (self.patient_id,))
            self.appointmentList = []
            result = self.db.c.fetchall()
            for i in result:
                self.appointmentList.append(i)
            print(" ")
            util.loader('Loading')
            print("\n")

            # Print appointments and options.
            apt = []
            for i in self.appointmentList:
                if i[-1] == 1:
                    status = "completed."
                elif i[-3] + i[-2] == 0:
                    status = "not yet confirmed."
                elif i[-3] == 1:
                    status = "confirmed."
                else:
                    status = "rejected."
                apt.append("Your appointment with Dr. " +
                           str(i[1]) + " " + str(i[2]) + " at " + str(i[3][:10]) + " is " + status)
            if len(apt) == 0:
                print("Sorry, you have no appointments at the moment.")
                print(" ")
                break
            apt.append("Back")
            # Redirects to appointment management.
            option = ui.ask_choice("Choose an appointment", choices=apt, sort=False)
            option = list.index(apt, option)
            if option < len(apt) - 1:
                # appointmentData is in the format like (1, 'Olivia', 'Cockburn', '12/19/2020 13:00:00', '12/19/2020 14:00:00', 0, 0).
                util.clear()
                appointmentData = self.appointmentList[option]
                print('Appointment Date: '+appointmentData[3][:10])
                print('Time Slot: '+appointmentData[3][-8:-3]+" - "+appointmentData[4][-8:-3])
                print('GP: Dr ' + appointmentData[1] + " "+ appointmentData[2])
                if appointmentData[-1] == 1:
                    print("This appointment is completed.")
                    aptid = (appointmentData[0],)
                    self.db.exec_one("SELECT clinical_notes FROM Appointment WHERE appointment_id = ?", aptid)
                    result = self.db.c.fetchone()
                    notes = result[0]
                    if not notes:
                        print("Sorry, you have no clinical notes for this appointment.")
                    else:
                        print("Clinical notes: " + notes)
                    while True:
                        option = ui.ask_yes_no("Do you want to be redirected to appointment list?", default=False)
                        if option:
                            util.clear()
                            break
                elif (appointmentData[-3] + appointmentData[-2]) == 0:
                    print("This appointment is not approved yet.")
                    apt = ["Cancel this appointment.", "Back."]
                    option = ui.ask_choice("Choose an option", choices=apt, sort=False)
                    option = list.index(apt, option)
                    if option == 0:
                        self.cancel_appointment(appointmentData[0])
                    continue
                elif appointmentData[-3] == 0 or appointmentData[-2] == 0:
                    if appointmentData[-3] == 0:
                        print("This appointment is rejected.\n")
                    elif appointmentData[-1] == 0:
                        print("This appointment is confirmed.\n")
                    apt = ["Reschedule this appointment.",
                           "Cancel this appointment.", "Back."]
                    option = ui.ask_choice("Choose an option", choices=apt, sort=False)
                    option = list.index(apt, option)
                    if option == 0:
                        self.reschedule_appointment(appointmentData[0])
                    elif option == 1:
                        self.cancel_appointment(appointmentData[0])
            else:
                util.clear()
                self.print_welcome()
                break

    def request_appointment(self):
        while True:
            apt = ["Book an appointment this month.", "Book an appointment next month.", "Back."]
            menu_choice = ui.ask_choice("Choose an appointment", choices=apt, sort=False)
            util.clear()
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
                                # check if the date is in YYYY-MM-DD format
                                year, month, day = select_date.split('-')
                                isValidDate = True
                                datetime.datetime(int(year), int(month), int(day))
                                fm_selected = datetime.datetime.strptime(
                                    select_date, '%Y-%m-%d').date()
                            except ValueError:
                                isValidDate = False
                            if not isValidDate:
                                # if not request user tries again
                                print("Sorry this value is not accepted - please use the YYYY-MM-DD format")
                                opts = ["Try again", "Back to booking options menu"]
                                navigate = ui.ask_choice("Choose an option", choices=opts, sort=False)
                                navigate = list.index(opts, navigate)
                                if navigate in [0, 1]:
                                    if navigate == 1:
                                        break
                                    elif navigate == 2:
                                        break
                            elif isValidDate and self.weekday_bookings_only(select_date):
                                if self.limit_appointment_bookings(select_date) == 0:
                                    if datetime.datetime.now().date() < fm_selected <= last_booking_date:
                                        # if all conditions are met list out appts
                                        util.clear()
                                        print('The date {} is valid. Listing appointments... \n'.format(
                                            select_date))
                                        util.loader('Loading')
                                        self.select_slots(select_date)
                                    elif fm_selected < datetime.datetime.now().date():
                                        print("Sorry, we are unable to book appointments for dates in the past")
                                    elif fm_selected == datetime.datetime.now().date():
                                        print(
                                            "Sorry, we are unable to book appointments on the day as we must give our GP's prior notice")
                                    elif datetime.datetime.now().date() < fm_selected > last_booking_date:
                                        print(
                                            "Sorry, we are unable to book appointments too far into the future.\n"
                                            "Please enter a valid date between today and the close of next month:",
                                            last_booking_date)
                                elif self.limit_appointment_bookings(select_date) > 0:
                                    # if patient already has an appt for that week request they book for another
                                    print(
                                        "Sorry you have already requested an appointment booked for this week. \nTo ensure that our GPs are able to see "
                                        "as many patients as possible and there is fair assignment in place, "
                                        "please select an alternative week where you"
                                        " do not currently have an appointment booked.")
                                    continue
                            elif isValidDate and not self.weekday_bookings_only(select_date) and \
                                    datetime.datetime.now().date() < fm_selected <= last_booking_date:
                                # if the date given is valid but a weekend print ---
                                print(
                                    "Sorry our surgery is closed on weekends - you are unable to request an "
                                    "appointment for this date \n"
                                    "Please refer to the calendar and request an appointment for a weekday\n")
                                continue
                            elif datetime.datetime.now().date() < fm_selected > last_booking_date:
                                # if the date is valid but too far into the future print and continue loop
                                print(
                                    "Sorry, we are unable to book appointments too far into the future.\n"
                                    "Please enter a valid date between today and the close of next month:",
                                    last_booking_date)
                                continue
                            else:
                                print(
                                    "This input will not be accepted im afraid - Please re-enter in YYYY-MM-DD format")
                        elif date_booker == 1:
                            break
            elif menu_choice == 2:
                util.clear()
                self.print_welcome()
                break
            else:
                print("System Failure: please restart")

    def limit_appointment_bookings(self, select_date):
        # queries the DB to see if a patient already has an appt between for a week they have selected
        day = select_date
        dt = datetime.datetime.strptime(day, '%Y-%m-%d')
        start = dt - td(days=dt.weekday())
        end = start + td(days=4)
        self.db.exec("""SELECT count(a.appointment_id) FROM Appointment AS A
                            LEFT JOIN Slots AS S
                            ON s.slot_id = a.slot_id
                            WHERE a.patient_id = '""" + str(self.patient_id) + """' AND
                            s.startTime BETWEEN '""" + str(start) + """' AND '""" + str(end) + """'""")
        result = self.db.c.fetchall()
        x = result[0]
        weekly_appointment_count = x[0]
        return weekly_appointment_count

    def receive_covid_notification(self):
        # queries the DB to see if a patient already has an appt between for a week they have selected
        self.db.exec("""SELECT date_of_birth, signUpDate FROM Users
                           WHERE userId = '""" + str(self.patient_id) + """'""")
        result = self.db.c.fetchall()
        x = result[0]
        date_of_birth = x[0]
        sign_up = x[1]
        sign_up_date = sign_up[:10]
        vaccinations = ["Pfizer-BioNTech", "Oxford University/AstraZeneca", "Moderna mRNA-1273"]
        chosen_vac = random.choice(vaccinations)
        if datetime.datetime.strptime(date_of_birth, '%Y-%m-%d').date() < datetime.datetime.now().date() - \
                datetime.timedelta(60 * 365) and datetime.datetime.strptime(sign_up_date, '%m-%d-%Y').date() \
                < datetime.datetime.now().date() - datetime.timedelta(1 * 31):
            vulnerable_individual = True
            print(colored('*COVID-19 status notification*', 'red',
                          attrs=['bold']))
            print(
                "-- You have been identified as a high risk patient to COVID-19 and have been invited to receive your "
                "first dose of the " + chosen_vac + " vaccination.\n- This classification has been made based on your "
                                                    "age and you have been on the waiting list for over 30 days (30 days since the date that you "
                                                    "registered with us).\n- Please request an appointment with one of our GP's and citing 'COVID-19 vaccination'"
                                                    " or 'COVID-19 Immunisation' so that you may be protected.\n- We look forward to hearing from you.\n")
        else:
            vulnerable_individual = False
            print("You have not been identified as a high risk patient to COVID-19. However you will be invited to "
                  "receive a vaccination in due course. Please stay at home and protect the NHS :)\n")
        return vulnerable_individual

    def high_risk_top_waitinglist_notification(self):
        # queries the DB to see if a patient already has an appt between for a week they have selected
        self.db.exec("""SELECT date_of_birth, signUpDate FROM Users
                            WHERE userId = '""" + str(self.patient_id) + """'""")
        result = self.db.c.fetchall()
        x = result[0]
        date_of_birth = x[0]
        sign_up = x[1]
        sign_up_date = sign_up[:10]
        vaccinations = ["Pfizer-BioNTech", "Oxford University/AstraZeneca"]
        chosen_vac = random.choice(vaccinations)
        if datetime.datetime.strptime(date_of_birth, '%Y-%m-%d').date() < datetime.datetime.now().date() - \
                datetime.timedelta(60 * 365) and datetime.datetime.strptime(sign_up_date, '%m-%d-%Y').date() \
                < datetime.datetime.now().date() - datetime.timedelta(1 * 31):
            high_risk_top_waitinglist = True
            print(colored('*COVID-19 status notification*', 'red',
                          attrs=['bold']))
            print(
                "-- You have been identified as a high risk patient to COVID-19 and have been invited to receive your "
                "first dose of the " + chosen_vac + " vaccination.\n- This classification has been made based on your "
                                                    "age and you have been on the waiting list for over 30 days (30 days since the date that you "
                                                    "registered with us).\n- Please request an appointment with one of our GP's and citing 'COVID-19 vaccination'"
                                                    " or 'COVID-19 Immunisation' so that you may be protected.\n- We look forward to hearing from you.\n")
        else:
            high_risk_top_waitinglist = False
        return high_risk_top_waitinglist

    def low_risk_notification(self):
        # queries the DB to see if a patient already has an appt between for a week they have selected
        self.db.exec("""SELECT date_of_birth, signUpDate FROM Users
                             WHERE userId = '""" + str(self.patient_id) + """'""")
        result = self.db.c.fetchall()
        x = result[0]
        date_of_birth = x[0]
        if datetime.datetime.strptime(date_of_birth, '%Y-%m-%d').date() > datetime.datetime.now().date() - \
                datetime.timedelta(60 * 365):
            low_risk_patient = True
            print(colored('*COVID-19 status notification*', 'green',
                          attrs=['bold']))
            print("-- In accordance with our system, you have been classified as a low-risk patient to COVID-19.\n"
                  "- However, you will receive an invite to have a vaccination in due course but we are currently "
                  "prioritising the vulnerable groups.\n- Please stay at home and protect the NHS! :)")
        else:
            low_risk_patient = False
        return low_risk_patient

    def covid_appt_count(self):
        # queries the DB to see number of COVID_19 related appts
        self.db.exec("""SELECT count(a.appointment_id) FROM Appointment AS a
                        LEFT JOIN slots s
                        ON a.slot_id = s.slot_id
                        WHERE a.patient_id = '""" + str(self.patient_id) + """'
                        and
                        a.reason = 'COVID-19 immunisation' or a.reason = 'COVID-19 vaccination'""")
        result = self.db.c.fetchall()
        tup = result[0]
        counter = tup[0]
        return counter

    def dismiss_covid_notification(self):
        # queries the DB to see if a patient already has an appt between for a week they have selected
        self.db.exec("""SELECT a.reason, s.endTime FROM Appointment AS a
        LEFT JOIN slots s
        ON a.slot_id = s.slot_id
        WHERE a.patient_id = '""" + str(self.patient_id) + """'
        and
        a.reason = 'COVID-19 immunisation' or a.reason = 'COVID-19 vaccination'""")
        result = self.db.c.fetchall()
        tup = result[0]
        end_time = tup[1]
        vaccination_time = end_time[:10]
        if datetime.datetime.strptime(vaccination_time, '%Y-%m-%d').date() < datetime.datetime.now().date():
            print(colored('*COVID-19 status notification*', 'green',
                          attrs=['bold']))
            print("-- Congratulations! You have now received you first dose of the "
                  "COVID-19 vaccine.\n- We will contact you again in 3 months time to receive your second dose.\n")
            immunised = True
        else:
            print(colored('*COVID-19 status notification*', 'red',
                          attrs=['bold']))
            print("-- You have an upcoming appointment to receive a COVID-19 vaccination.\n- Please check your "
                  "'View appointments' tab for further details. \n")
            immunised = False
        return immunised

    def weekday_bookings_only(self, chosen_date):
        # restrict bookings to weekdays only using this function
        x = datetime.datetime.strptime(chosen_date, '%Y-%m-%d').weekday()
        if x < 5:
            status = True
        else:
            status = False
        return status

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
        print("\n\nPlease select an appointment time:")
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
        df1.index += 1
        print("\n")
        self.display_opening_hours(select_date)
        print(colored('Available slots on the ' + select_date + ' ', 'green',
                      attrs=['bold']))
        print(tabulate(df1, headers='keys',
                       tablefmt='grid', showindex=True))
        print(str(num + 1) + ". Back")
        return [result_session, available_session]

    def select_slots(self, select_date):
        while True:
            # self.display_opening_hours(select_date)
            output = self.available_session(select_date)
            result = output[1]
            session = output[0]
            try:
                booked_slot = int(input("Enter your option : "))

                if booked_slot == (len(result) + 1):
                    break
                elif booked_slot in range(9):
                    # Assign GP6 to this appointment temporarily.
                    # selected_session = available_session[booked_slot - 1][:2]
                    # ask the patient to input any symptoms they may have or default value is 'none'
                    symptoms = input("Please list any symptoms or concerns you may have so that we may"
                                     " inform your assigned GP...\n"
                                     "or hit enter if you do not want to disclose now: \n ")
                    key = session[booked_slot - 1][:2]
                    slot = result[key][0][1]
                    gp = result[key][0][0]
                    gp_name = self.db.gp_name(gp)
                    a = (self.patient_id, slot, gp, symptoms)
                    # Insert request into database.
                    print("Do you confirm that you want to book this appointment?")

                    option = ui.ask_choice("Choose an option", choices=["Yes", "No"], sort=False)
                    option = list.index(["Yes", "No"], option)
                    if option == 0:
                        print("- Appointment Date: " + select_date)
                        print("- Time Slot: " + session[booked_slot-1])
                        print("- GP: Dr " + gp_name[0] + " " + gp_name[1])
                        if self.tobecanceled > 0:
                            self.db.reschedule(a, self.tobecanceled)
                            self.tobecanceled = -1
                            print(
                                "SUCCESS - \nYou have successfully rescheduled an appointments with Dr " + str(
                                    gp_name[0]) + " " + str(
                                    gp_name[1]) + ", You will be alerted once your appointment is confirmed")
                            util.clear()
                        else:
                            self.db.exec_one(
                                "INSERT INTO Appointment(patient_id,slot_id,gp_id,reason) Values (?,?,?,?)", a)
                            print(
                                "SUCCESS - \nYou have successfully requested an appointments with Dr " + str(
                                    gp_name[0]) + " " + str(
                                    gp_name[1]) + ", You will be alerted once your appointment is confirmed")
                            util.clear()
                    self.print_welcome()
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
            util.clear()
            break

    def view_prescription(self):
        # Fetch prescriptions from db.
        try:
            self.db.exec(
                "SELECT p.medicine_name, p.treatment_description, p.pres_frequency_in_days, p.startDate, p.expiryDate, p.prescription_id, p.appointment_id FROM Prescription AS P "
                "LEFT JOIN Appointment as a "
                "ON a.appointment_id = p.appointment_id "
                "LEFT JOIN Users as u "
                "ON a.patient_id = u.userId "
                "WHERE u.userId = '""" + str(self.patient_id) + """'""")
            output = self.db.c.fetchall()
            index_8 = ["Medicine Name", "Treatment Desc", "Frequency of presc renewal (days)", "Start Date", "Expiry Date",
                       "Prescription ID", "Appointment ID"]
            df4 = DataFrame(output)
            df4.columns = index_8
            df4.index += 1
            pd.DataFrame(df4)
            print(" ")
            util.loader('Loading')
            print("\n")
            util.clear()
            # print prescriptions out as one table
            print(colored('Prescription Information', 'green',
                          attrs=['bold']))
            print(tabulate(df4, headers='keys',
                           tablefmt='grid', showindex=True))
            presc = ["Download Prescriptions as (.csv)", "Download Prescriptions as (.txt)", "Back"]
            presc_opts = ui.ask_choice("Choose an option", choices=presc, sort=False)
            presc_opts = list.index(presc, presc_opts)

            #  method for printing out prescriptions as either .txt or .csv
            def print_prescription(data_type):
                if data_type == "csv":
                    try:
                        #  create directory for downloaded files
                        directory = "downloaded_data"
                        directory2 = "Prescriptions"
                        parent_dir = '../programming-cw'
                        path = os.path.join(parent_dir, directory)
                        final_path = os.path.join(path, directory2)
                        os.makedirs(final_path)
                        # save prescription in directory  as a .csv
                        with open("downloaded_data/Prescriptions/myprescriptions." + data_type, 'w',
                                  newline='') as f:
                            thewriter = csv.writer(f)
                            thewriter.writerow(index_8)
                            for i in output:
                                thewriter.writerow([i[0], i[1], i[2], str(i[3]), i[4], i[5], str(i[6])])
                            f.close()
                            print(" ")
                            util.loader('Downloading')
                            print("\n")
                            print("...Your prescription has been downloaded successfully\n")
                            print(" ")
                            time.sleep(1.5)
                    except FileExistsError:
                        #  unless directory already exists
                        # save to existing Prescription folder as a .csv
                        with open("downloaded_data/Prescriptions/myprescriptions." + data_type, 'w',
                                  newline='') as f:
                            thewriter = csv.writer(f)
                            thewriter.writerow(index_8)
                            for i in output:
                                thewriter.writerow([i[0], i[1], i[2], str(i[3]), i[4], i[5], str(i[6])])
                            f.close()
                            print(" ")
                            util.loader('Downloading')
                            print("\n")
                            print("...Your prescription has been downloaded successfully\n")
                            print(" ")
                            time.sleep(1.5)
                elif data_type == "txt":
                    try:
                        directory = "downloaded_data"
                        directory2 = "Prescriptions"
                        parent_dir = '../programming-cw'
                        path = os.path.join(parent_dir, directory)
                        final_path = os.path.join(path, directory2)
                        os.makedirs(final_path)
                        # save to Prescription folder as a .txt
                        with open("downloaded_data/Prescriptions/myprescriptions." + data_type, 'w',
                                  newline='') as f:
                            f.write("Your prescriptions are as follows:\n"
                                    "\n")
                            f.write("\n")
                            f.write(df4.to_string(header=index_8, index=True))
                            f.close()
                            print(" ")
                            util.loader('Downloading')
                            print("\n")
                            print("...Your prescription has been downloaded successfully\n")
                            print(" ")
                            time.sleep(1.5)
                    except FileExistsError:
                        #  unless directory already exists
                        # save to existing Prescription folder as a .csv
                        with open("downloaded_data/Prescriptions/myprescriptions." + data_type, 'w',
                                  newline='') as f:
                            f.write("Your prescriptions are as follows:\n"
                                    "\n")
                            f.write("\n")
                            f.write(df4.to_string(header=index_8, index=True))
                            f.close()
                            print(" ")
                            util.loader('Downloading')
                            print("\n")
                            print("...Your prescription has been downloaded successfully\n")
                            print(" ")
                            time.sleep(1.5)
            # options
            if presc_opts in [0, 1, 2]:
                if presc_opts == 0:
                    print_prescription("csv")
                    util.clear()
                    self.print_welcome()
                elif presc_opts == 1:
                    print_prescription("txt")
                    util.clear()
                    self.print_welcome()
                elif presc_opts == 2:
                    util.clear()
                    self.print_welcome()
        except ValueError:
            print(" ")
            util.loader('Loading')
            print(" ")
            # no prescription in the DB so return ---
            print("\nSorry - you currently do not have any prescriptions from our GP's to display\n")

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
                       tablefmt='grid', showindex=False))
        return output[0]
