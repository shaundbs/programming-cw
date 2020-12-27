import sqlite3
# hide password when inputting
from database import Database
from email_generator import Emails
import re
import datetime as datetime
import getpass
import bcrypt
import calendar
from tabulate import tabulate
from termcolor import colored
from pandas import DataFrame
import random
import timedelta


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

        # Encode pw and insert user credentials into db.
        pWord = pWord.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pWord, salt)
        aType = "patient"
        time_now = datetime.datetime.now()
        date_time = time_now.strftime("%m-%d-%Y %H:%M:%S")
        a = [(fName, lName, email, hashed, aType, date_time,), ]
        db.exec_many(
            "INSERT INTO Users(firstName,lastName,email,password,accountType,signUpDate) Values (?,?,?,?,?,?)", a)
        Emails.registration_email(email, fName, lName, "patient")

    def select_options(self):
        while True:
            print('1. Request Appointments')
            print('2. View Appointments')
            print('3. View Prescription')
            print('4. Log out')
            option = input('Please choose an option: ')
            if option == '1':
                self.request_appointment()
            elif option == '2':
                self.view_appointment()
            elif option == '3':
                self.view_prescription()
            elif option == '4':
                break
            else:
                print("Wrong input. Please try again.")

    def request_appointment(self):
        while True:
            print("\n"
                  "1. Book an appointment this month \n"
                  "2. Book an appointment next month \n"
                  "3. Exit \n")
            menu_choice = input("Please enter an option: ")
            if menu_choice == '2':
                # print calendar for this month
                this_m = datetime.datetime.today()
                one_month = datetime.timedelta(1 * 365 / 12)
                next_m = this_m + one_month
                year_nm = datetime.datetime.date(next_m).strftime("%Y")
                month_nm = datetime.datetime.date(next_m).strftime("%m")
                day_nm = datetime.datetime.date(next_m).strftime("%d")
                c = calendar.TextCalendar(calendar.MONDAY)
                year_input, month_input, day_input = int(
                    year_nm), int(month_nm), int(day_nm)
                calendar_month = c.formatmonth(
                    year_input, month_input, day_input, 0)
                print(calendar_month)
                try:
                    while True:
                        #  user enters the date date they would like to book a GP on
                        select_date = input(
                            "Please enter a valid date in YYYY-MM-DD format between now and the close of next month:\n")
                        fm_date = datetime.datetime.strptime(
                            select_date, '%Y-%m-%d').date()
                        try:
                            #   exception handling so that patients can only book appointments for the end of the
                            #   following month

                            if datetime.datetime.now().date() < datetime.datetime.strptime(select_date,
                               '%Y-%m-%d').date() < datetime.datetime.now().date() + one_month:
                                datetime.datetime.strptime(select_date, '%Y-%m-%d')

                            # check if the date entered by the user fits the condition and is valid
                                print('The date {} is valid. Listing appointments... \n'.format(select_date))

                            # get datetime object of the first and last appointments on that day = Opening hours
                                db2 = Database()
                                db2.exec_one("SELECT min(startTime), max(endTime) FROM SLOTS "
                                             "WHERE startTime like (?)", ("%" + str(fm_date) + "%",))
                                index_2 = ["Opening Time", "Closing time"]
                                output = db2.c.fetchall()
                                op_hours = output[0]

                            # create table with opening hour info
                                df2 = DataFrame(output)
                                df2.columns = index_2
                                print(colored('Opening hours: ' + select_date + ' ', 'green', attrs=['bold']))
                                print(tabulate(df2, headers='keys', tablefmt='fancy_grid', showindex=False))

                            # query the number of Gp's available for each timeslot on the selected day
                                db = Database()
                                db.exec(
                                    "SELECT s.startTime, s.endTime, COUNT(s.startTime) as 'No. GPs available' "
                                    "FROM SLOTS S "
                                    "CROSS JOIN Users U "
                                    "LEFT JOIN APPOINTMENT A "
                                    "ON S.slot_id = A.slot_id "
                                    "AND A.gp_id = U.userId "
                                    "AND((A.IS_CONFIRMED =0 AND A.IS_REJECTED=0) OR(A.is_confirmed = 1)) "
                                    # EITHER UNCONFIRMED/UNREJECTED OR CONFIRMED we wil remove.
                                    "LEFT JOIN gp_time_off gpto "  # IF SLOT FALLS BETWEEN START AND ENDTIME
                                    # OF GP TIME OFF WE WILL REMOVE
                                    "ON datetime(S.startTime) >= datetime(GPTO.startTime) AND "
                                    "datetime(S.startTime) < datetime(GPTO.endTime) "
                                    "AND GPTO.gp_id = U.userId "
                                    "WHERE U.accountType ='gp' "  # GP
                                    "and "
                                    "u.is_active = 1 "  # active GP
                                    "AND DATE(S.startTime) = DATE('" + str(fm_date) + "') "
                                    # limit to date we looking for
                                    "AND A.GP_ID IS NULL "  # remove gps with appts
                                    "AND GPTO.GP_ID IS NULL "
                                    # remove anyone with time off schedule over that appt time
                                    "GROUP BY s.startTime "
                                    "HAVING s.startTime BETWEEN '" +
                                    op_hours[0] + "' AND '" + op_hours[1] + "'")

                                # create table with output from the above query

                                index_1 = ["Start time", "End time", "No. GP's available"]
                                result = db.c.fetchall()
                                df1 = DataFrame(result)
                                df1.columns = index_1

                                print(colored('Appointments available on the ' + select_date + ' ', 'green',
                                              attrs=['bold']))
                                print(tabulate(df1, headers='keys', tablefmt='fancy_grid', showindex=True))

                                # print time slots and user will use the table above as a reference to select a time
                                # when at least one GP is available

                                print("\n"
                                      "Please select an appointment time: \n")
                                print("1. 09:00-10:00")
                                print("2. 10:00-11:00")
                                print("3. 11:00-12:00")
                                print("4. 12:00-13:00")
                                print("5. 13:00-14:00")
                                print("6. 14:00-15:00")
                                print("7. 15:00-16:00")
                                print("8. 16:00-17:00 \n")
                                # patient enters the number that corresponds to the time slot they would like to book
                                booked_slot = int(
                                    input("\n"
                                          "Enter your option : "))
                                print("\n")

                                # covert timeslots throughout the day to datetime objects
                                apt_time = datetime.datetime.strptime(op_hours[0], '%Y-%m-%d %H:%M:%S')
                                total = []

                                for i in range(8):
                                    db6 = Database()
                                    db6.exec("SELECT s.startTime, s.endTime, COUNT(s.startTime) as 'No. GPs available',"
                                             " s.slot_id "
                                             "FROM SLOTS S "
                                             "CROSS JOIN Users U "
                                             "LEFT JOIN APPOINTMENT A "
                                             "ON S.slot_id = A.slot_id "
                                             "AND A.gp_id = U.userId "
                                             "AND((A.IS_CONFIRMED =0 AND A.IS_REJECTED=0) OR(A.is_confirmed = 1)) "
                                             "LEFT JOIN gp_time_off gpto "
                                             "ON datetime(S.startTime) >= datetime(GPTO.startTime) AND "
                                             "datetime(S.startTime) < datetime(GPTO.endTime) "
                                             "AND GPTO.gp_id = U.userId "
                                             "WHERE U.accountType ='gp' "
                                             "and "
                                             "u.is_active = 1 "
                                             "AND DATE(S.startTime) = DATE('" + str(fm_date) + "') "
                                             "AND A.GP_ID IS NULL "
                                             "AND GPTO.GP_ID IS NULL "
                                             "GROUP BY s.startTime "
                                             "HAVING s.startTime = '" + str(apt_time) + "'")
                                    output_4 = db6.c.fetchall()
                                    no_gps_available = output_4[0]
                                    total.append(no_gps_available[2])
                                    apt_time += timedelta.Timedelta(hours=1)

                                # exception handling - make sure there is at least 1 GP available for each timeslot
                                # and if there is not when the user selects that time they are notified it can't be
                                # booked and return to the selection screen

                                if booked_slot == 1 and total[0] > 0:
                                    print("Good news...we have " + str(total[0]) +
                                          " GPs available to see you at this time")
                                elif booked_slot == 2 and total[1] > 0:
                                    print("Good news...we have " + str(total[1]) +
                                          " GPs available to see you at this time")
                                elif booked_slot == 3 and total[2] > 0:
                                    print("Good news...we have " + str(total[2]) +
                                          " GPs available to see you at this time")
                                elif booked_slot == 4 and total[2] > 0:
                                    print("Good news...we have " + str(total[3]) +
                                          " GPs available to see you at this time")
                                elif booked_slot == 5 and total[4] > 0:
                                    print("Good news...we have " + str(total[4]) +
                                          " GPs available to see you at this time")
                                elif booked_slot == 6 and total[5] > 0:
                                    print("Good news...we have " + str(total[5]) +
                                          " GPs available to see you at this time")
                                elif booked_slot == 7 and total[6] > 0:
                                    print("Good news...we have " + str(total[6]) +
                                          " GPs available to see you at this time")
                                elif booked_slot == 8 and total[7] > 0:
                                    print("Good news...we have " + str(total[7]) +
                                          " GPs available to see you at this time")
                                # elif not isinstance(booked_slot, int):
                                #     print("No, please enter a number between 0-7")
                                #     break
                                else:
                                    print("There are no GP's available to see you at this time -  \n please"
                                          "select another time slot or choose another day")
                                    break

                                # get the name of active GPs that are available for each time slot
                                db5 = Database()
                                db5.exec(
                                    "SELECT u.firstName, u.lastName "
                                    "FROM SLOTS S "
                                    "CROSS JOIN Users U "
                                    "LEFT JOIN APPOINTMENT A "
                                    "ON S.slot_id= A.slot_id "
                                    "AND A.gp_id = U.userId "
                                    "AND ((A.IS_CONFIRMED =0 AND A.IS_REJECTED=0) OR (A.is_confirmed=1)) "
                                    #  EITHER UNCONFIRMED/UNREJECTED OR CONFIRMED we wil remove.
                                    "LEFT JOIN gp_time_off gpto "  # IF SLOT FALLS BETWEEN START AND ENDTIME
                                    # OF GP TIME OFF WE WILL REMOVE
                                    "ON datetime(S.startTime) >= datetime(GPTO.startTime) AND "
                                    "datetime(s.startTime) < datetime(GPTO.endTime) "
                                    "AND GPTO.gp_id = U.userId "
                                    "WHERE U.accountType='gp' "  # GP
                                    "and "
                                    "u.is_active = 1 "  # active GP
                                    "AND DATE(S.startTime) = DATE('" + str(fm_date) + "') "
                                    # limit to date we looking for
                                    "AND A.GP_ID IS NULL "  # remove gps with appts
                                    "AND GPTO.GP_ID IS NULL "
                                    # remove anyone with time off schedule over that appt time
                                    "GROUP BY u.firstName "
                                    "HAVING s.startTime = '" +
                                    op_hours[0] + "'")
                                med_professionals = db5.c.fetchall()

                                # print the names of the GPs available for that timeslot for the patient to view
                                for i in med_professionals:
                                    available_gp = i[0] + ' ' + i[1]
                                    print("\n"
                                          "Dr. " + available_gp + " is available.")

                                # randomly select a GP from the options available during that timeslot
                                assigned_gp = random.choice(med_professionals)
                                print("\nYou have been assigned: Dr. " + assigned_gp[0] + ' ' + assigned_gp[1])
                                print("\n")

                                # get slot_id for the selected timeslot
                                db3 = Database()
                                db3.exec("SELECT s.startTime, s.endTime, COUNT(s.startTime) as 'No. GPs available',"
                                         " s.slot_id "
                                         "FROM SLOTS S "
                                         "CROSS JOIN Users U "
                                         "LEFT JOIN APPOINTMENT A "
                                         "ON S.slot_id = A.slot_id "
                                         "AND A.gp_id = U.userId "
                                         "AND((A.IS_CONFIRMED =0 AND A.IS_REJECTED=0) OR(A.is_confirmed = 1)) "
                                         "LEFT JOIN gp_time_off gpto "
                                         "ON datetime(S.startTime) >= datetime(GPTO.startTime) AND "
                                         "datetime(S.startTime) < datetime(GPTO.endTime) "
                                         "AND GPTO.gp_id = U.userId "
                                         "WHERE U.accountType ='gp' "
                                         "and "
                                         "u.is_active = 1 "
                                         "AND DATE(S.startTime) = DATE('" + str(fm_date) + "') "
                                         "AND A.GP_ID IS NULL "
                                         "AND GPTO.GP_ID IS NULL "
                                         "GROUP BY s.startTime "
                                         "HAVING s.startTime = '" +
                                         op_hours[0] + "'")
                                output_2 = db3.c.fetchall()
                                no_gps_available = output_2[0]

                                # get gp_id for the GP assigned to the appointment
                                db4 = Database()
                                db4.exec("SELECT userId FROM Users "
                                         "WHERE firstName = '" + assigned_gp[0] + "' "
                                         "AND "
                                         "lastName = '" + assigned_gp[1] + "'")
                                output_3 = db4.c.fetchone()
                                assigned_gp_id = output_3[0]

                                # ask the patient to input any symptoms they may have or default value is 'none'
                                symptoms = input("Please list any symptoms or concerns you may have so that we may"
                                                 " inform your assigned GP... \n"
                                                 "or hit enter if you do not want to disclose now: \n ")
                                a = [(self.patient_id, assigned_gp_id, no_gps_available[3], symptoms), ]
                                # insert the amalgamation of data into the appointments table as one record
                                db.exec_many(
                                    "INSERT INTO Appointment(patient_id,gp_id,slot_id,reason) Values (?,?,?,?)", a)
                                break
                            else:
                                print("We are unable to book appointments in the past or too far in the future"
                                      "Please enter a valid date between today and the close of next month")
                                continue
                        except ValueError:
                            print(
                                "This value is not accepted. Please enter a number from 1-8")
                except ValueError:
                    print("Wrong value entered, try again")
            elif menu_choice == '1':
                time_now = datetime.datetime.now()
                year_now = datetime.datetime.date(time_now).strftime("%Y")
                month_now = datetime.datetime.date(time_now).strftime("%m")
                day_now = datetime.datetime.date(time_now).strftime("%d")
                one_month = datetime.timedelta(1 * 365 / 12)
                c = calendar.TextCalendar(calendar.MONDAY)
                year_input, month_input, day_input = int(
                    year_now), int(month_now), int(day_now)
                calendar_month = c.formatmonth(
                    year_input, month_input, day_input, 0)
                print(calendar_month)
                try:
                    while True:
                        #  user enters the date date they would like to book a GP on
                        select_date = input(
                            "Please enter a valid date in YYYY-MM-DD format between now and the close of next month:\n")
                        fm_date = datetime.datetime.strptime(
                            select_date, '%Y-%m-%d').date()
                        try:
                            #   exception handling so that patients can only book appointments for the end of the
                            #   following month

                            if datetime.datetime.now().date() < datetime.datetime.strptime(select_date,
                               '%Y-%m-%d').date() < datetime.datetime.now().date() + one_month:
                                datetime.datetime.strptime(select_date, '%Y-%m-%d')

                                # check if the date entered by the user fits the condition and is valid
                                print('The date {} is valid. Listing appointments... \n'.format(select_date))

                                # get datetime object of the first and last appointments on that day = Opening hours
                                db2 = Database()
                                db2.exec_one("SELECT min(startTime), max(endTime) FROM SLOTS "
                                             "WHERE startTime like (?)", ("%" + str(fm_date) + "%",))
                                index_2 = ["Opening Time", "Closing time"]
                                output = db2.c.fetchall()
                                op_hours = output[0]

                                # create table with opening hour info
                                df2 = DataFrame(output)
                                df2.columns = index_2
                                print(colored('Opening hours: ' + select_date + ' ', 'green', attrs=['bold']))
                                print(tabulate(df2, headers='keys', tablefmt='fancy_grid', showindex=False))

                                # query the number of Gp's available for each timeslot on the selected day
                                db = Database()
                                db.exec(
                                    "SELECT s.startTime, s.endTime, COUNT(s.startTime) as 'No. GPs available' "
                                    "FROM SLOTS S "
                                    "CROSS JOIN Users U "
                                    "LEFT JOIN APPOINTMENT A "
                                    "ON S.slot_id = A.slot_id "
                                    "AND A.gp_id = U.userId "
                                    "AND((A.IS_CONFIRMED =0 AND A.IS_REJECTED=0) OR(A.is_confirmed = 1)) "
                                    # EITHER UNCONFIRMED/UNREJECTED OR CONFIRMED we wil remove.
                                    "LEFT JOIN gp_time_off gpto "  # IF SLOT FALLS BETWEEN START AND ENDTIME
                                    # OF GP TIME OFF WE WILL REMOVE
                                    "ON datetime(S.startTime) >= datetime(GPTO.startTime) AND "
                                    "datetime(S.startTime) < datetime(GPTO.endTime) "
                                    "AND GPTO.gp_id = U.userId "
                                    "WHERE U.accountType ='gp' "  # GP
                                    "and "
                                    "u.is_active = 1 "  # active GP
                                    "AND DATE(S.startTime) = DATE('" + str(fm_date) + "') "
                                    # limit to date we looking for
                                    "AND A.GP_ID IS NULL "  # remove gps with appts
                                    "AND GPTO.GP_ID IS NULL "
                                    # remove anyone with time off schedule over that appt time
                                    "GROUP BY s.startTime "
                                    "HAVING s.startTime BETWEEN '" + op_hours[0] + "' AND '" + op_hours[1] + "'")

                                # create table with output from the above query

                                index_1 = ["Start time", "End time", "No. GP's available"]
                                result = db.c.fetchall()
                                df1 = DataFrame(result)
                                df1.columns = index_1

                                print(colored('Appointments available on the ' + select_date + ' ', 'green',
                                              attrs=['bold']))
                                print(tabulate(df1, headers='keys', tablefmt='fancy_grid', showindex=True))

                                # print time slots and user will use the table above as a reference to select a time
                                # when at least one GP is available

                                print("\n"
                                      "Please select an appointment time: \n")
                                print("1. 09:00-10:00")
                                print("2. 10:00-11:00")
                                print("3. 11:00-12:00")
                                print("4. 12:00-13:00")
                                print("5. 13:00-14:00")
                                print("6. 14:00-15:00")
                                print("7. 15:00-16:00")
                                print("8. 16:00-17:00 \n")
                                # patient enters the number that corresponds to the time slot they would like to book
                                booked_slot = int(
                                    input("\n"
                                          "Enter your option : "))
                                print("\n")

                                # covert timeslots throughout the day to datetime objects
                                apt_time = datetime.datetime.strptime(op_hours[0], '%Y-%m-%d %H:%M:%S')
                                total = []

                                for i in range(8):
                                    db6 = Database()
                                    db6.exec("SELECT s.startTime, s.endTime, COUNT(s.startTime) as 'No. GPs available',"
                                             " s.slot_id "
                                             "FROM SLOTS S "
                                             "CROSS JOIN Users U "
                                             "LEFT JOIN APPOINTMENT A "
                                             "ON S.slot_id = A.slot_id "
                                             "AND A.gp_id = U.userId "
                                             "AND((A.IS_CONFIRMED =0 AND A.IS_REJECTED=0) OR(A.is_confirmed = 1)) "
                                             "LEFT JOIN gp_time_off gpto "
                                             "ON datetime(S.startTime) >= datetime(GPTO.startTime) AND "
                                             "datetime(S.startTime) < datetime(GPTO.endTime) "
                                             "AND GPTO.gp_id = U.userId "
                                             "WHERE U.accountType ='gp' "
                                             "and "
                                             "u.is_active = 1 "
                                             "AND DATE(S.startTime) = DATE('" + str(fm_date) + "') "
                                             "AND A.GP_ID IS NULL "
                                             "AND GPTO.GP_ID IS NULL "
                                             "GROUP BY s.startTime "
                                             "HAVING s.startTime = '" + str(apt_time) + "'")
                                    output_4 = db6.c.fetchall()
                                    no_gps_available = output_4[0]
                                    total.append(no_gps_available[2])
                                    apt_time += timedelta.Timedelta(hours=1)

                                # exception handling - make sure there is at least 1 GP available for each timeslot
                                # and if there is not when the user selects that time they are notified it can't be
                                # booked and return to the selection screen

                                if booked_slot == 1 and total[0] > 0:
                                    print("Good news...we have " + str(total[0]) +
                                          " GPs available to see you at this time")
                                elif booked_slot == 2 and total[1] > 0:
                                    print("Good news...we have " + str(total[1]) +
                                          " GPs available to see you at this time")
                                elif booked_slot == 3 and total[2] > 0:
                                    print("Good news...we have " + str(total[2]) +
                                          " GPs available to see you at this time")
                                elif booked_slot == 4 and total[2] > 0:
                                    print("Good news...we have " + str(total[3]) +
                                          " GPs available to see you at this time")
                                elif booked_slot == 5 and total[4] > 0:
                                    print("Good news...we have " + str(total[4]) +
                                          " GPs available to see you at this time")
                                elif booked_slot == 6 and total[5] > 0:
                                    print("Good news...we have " + str(total[5]) +
                                          " GPs available to see you at this time")
                                elif booked_slot == 7 and total[6] > 0:
                                    print("Good news...we have " + str(total[6]) +
                                          " GPs available to see you at this time")
                                elif booked_slot == 8 and total[7] > 0:
                                    print("Good news...we have " + str(total[7]) +
                                          " GPs available to see you at this time")
                                else:
                                    print("There are no GP's available to see you at this time -  \n please"
                                          "select another time slot or choose another day")
                                    break

                                # get the name of active GPs that are available for each time slot
                                db5 = Database()
                                db5.exec(
                                    "SELECT u.firstName, u.lastName "
                                    "FROM SLOTS S "
                                    "CROSS JOIN Users U "
                                    "LEFT JOIN APPOINTMENT A "
                                    "ON S.slot_id= A.slot_id "
                                    "AND A.gp_id = U.userId "
                                    "AND ((A.IS_CONFIRMED =0 AND A.IS_REJECTED=0) OR (A.is_confirmed=1)) "
                                    #  EITHER UNCONFIRMED/UNREJECTED OR CONFIRMED we wil remove.
                                    "LEFT JOIN gp_time_off gpto "  # IF SLOT FALLS BETWEEN START AND ENDTIME
                                    # OF GP TIME OFF WE WILL REMOVE
                                    "ON datetime(S.startTime) >= datetime(GPTO.startTime) AND "
                                    "datetime(s.startTime) < datetime(GPTO.endTime) "
                                    "AND GPTO.gp_id = U.userId "
                                    "WHERE U.accountType='gp' "  # GP
                                    "and "
                                    "u.is_active = 1 "  # active GP
                                    "AND DATE(S.startTime) = DATE('" + str(fm_date) + "') "
                                    # limit to date we looking for
                                    "AND A.GP_ID IS NULL "  # remove gps with appts
                                    "AND GPTO.GP_ID IS NULL "
                                    # remove anyone with time off schedule over that appt time
                                    "GROUP BY u.firstName "
                                    "HAVING s.startTime = '" + op_hours[0] + "'")
                                med_professionals = db5.c.fetchall()

                                # print the names of the GPs available for that timeslot for the patient to view
                                for i in med_professionals:
                                    available_gp = i[0] + ' ' + i[1]
                                    print("\n"
                                          "Dr. " + available_gp + " is available.")

                                # randomly select a GP from the options available during that timeslot
                                assigned_gp = random.choice(med_professionals)
                                print("\nYou have been assigned: Dr. " + assigned_gp[0] + ' ' + assigned_gp[1])
                                print("\n")

                                # get slot_id for the selected timeslot
                                db3 = Database()
                                db3.exec("SELECT s.startTime, s.endTime, COUNT(s.startTime) as 'No. GPs available',"
                                         " s.slot_id "
                                         "FROM SLOTS S "
                                         "CROSS JOIN Users U "
                                         "LEFT JOIN APPOINTMENT A "
                                         "ON S.slot_id = A.slot_id "
                                         "AND A.gp_id = U.userId "
                                         "AND((A.IS_CONFIRMED =0 AND A.IS_REJECTED=0) OR(A.is_confirmed = 1)) "
                                         "LEFT JOIN gp_time_off gpto "
                                         "ON datetime(S.startTime) >= datetime(GPTO.startTime) AND "
                                         "datetime(S.startTime) < datetime(GPTO.endTime) "
                                         "AND GPTO.gp_id = U.userId "
                                         "WHERE U.accountType ='gp' "
                                         "and "
                                         "u.is_active = 1 "
                                         "AND DATE(S.startTime) = DATE('" + str(fm_date) + "') "
                                         "AND A.GP_ID IS NULL "
                                         "AND GPTO.GP_ID IS NULL "
                                         "GROUP BY s.startTime "
                                         "HAVING s.startTime = '" + op_hours[0] + "'")
                                output_2 = db3.c.fetchall()
                                no_gps_available = output_2[0]

                                # get gp_id for the GP assigned to the appointment
                                db4 = Database()
                                db4.exec("SELECT userId FROM Users "
                                         "WHERE firstName = '" + assigned_gp[0] + "' "
                                         "AND "
                                         "lastName = '" + assigned_gp[1] + "'")
                                output_3 = db4.c.fetchone()
                                assigned_gp_id = output_3[0]

                                # ask the patient to input any symptoms they may have or default value is 'none'
                                symptoms = input("Please list any symptoms or concerns you may have so that we may"
                                                 " inform your assigned GP... "
                                                 "or hit enter if you do not want to disclose now")
                                a = [(self.patient_id, assigned_gp_id, no_gps_available[3], symptoms), ]
                                # insert the amalgamation of data into the appointments table as one record
                                db.exec_many(
                                    "INSERT INTO Appointment(patient_id,gp_id,slot_id,reason) Values (?,?,?,?)", a)
                                break
                            else:
                                print("We are unable to book appointments in the past or too far in the future"
                                      "Please enter a valid date between today and the close of next month")
                        except ValueError:
                            print(
                                "This value is not accepted. Please enter a number from 1-8:")
                except ValueError:
                    print("Wrong value entered, try again")
            elif menu_choice == '3':
                break
            else:
                print('Wrong input. Please try again.')

            # fix timeslot loop so that it goes back to the timeslots instead of calendar
            # limit on no of appointments per week



    def view_appointment(self):
        a = [(self.patient_id), ]
        db = Database()
        while True:
            db.exec_one(
                "SELECT a.appointment_Id, u.firstName, u.lastName, s.startTime, s.endTime, a.is_confirmed, a.is_rejected FROM Appointment a, Slots s, Users u WHERE a.gp_id = u.userId AND a.slot_id = s.slot_id And a.patient_id = ? ORDER BY startTime",
                a)
            self.appointmentList = []
            result = db.c.fetchall()
            for i in result:
                self.appointmentList.append(i)

            print("")
            num = 1
            for i in self.appointmentList:
                if i[-2] + i[-1] == 0:
                    status = "not yet confirmed."
                elif i[-2] == 1:
                    status = "confirmed."
                else:
                    status = "rejected."
                print(str(num) + ". Your appointment with Dr " +
                      str(i[1]) + " " + str(i[2]) + " at " + str(i[3][:10]) + " is " + status)
                num += 1
            print(str(num) + ". Back")
            option = int(input("You choose number: "))

            if option == num:
                break
            elif option in range(1, num):
                self.appointment_options(self.appointmentList[option - 1])

    def appointment_options(self, appointmentData):
        # appointmentData is in the format like (1, 'Olivia', 'Cockburn', '12/19/2020 13:00:00', '12/19/2020 14:00:00', 0, 0).
        if (appointmentData[-2] + appointmentData[-1]) == 0:
            print("\nThis appointment is not approved yet.\n1. Back")
            while True:
                option = input("You choose number: ")
                if option == "1":
                    break

        elif appointmentData[-2] == 0:
            print(
                "\nThis appointment is confirmed.\n1. Reschedule this appointment.\n2. Cancel this appointment.\n3. Back")
            self.appointment_options_select(appointmentData[0])

        elif appointmentData[-1] == 0:
            print(
                "\nThis appointment is rejected.\n1. Reschedule this appointment.\n2. Cancel this appointment.\n3. Back")
            self.appointment_options_select(appointmentData[0])

    def appointment_options_select(self, appointmentId):
        while True:
            option = input("You choose number: ")
            if option == "1":
                self.reschedule_appointment(appointmentId)
                break
            elif option == "2":
                self.cancel_appointment(appointmentId)
                break
            elif option == "3":
                break

    def reschedule_appointment(self, appointmentNo):
        while True:
            print("1. Book an appointment this month \n"
                  "2. Book an appointment next month \n"
                  "3. Exit")
            m = input("Please enter an option: ")
            if m == "1":
                a = datetime.datetime.today()
            elif m == "2":
                a = datetime.datetime.today() + datetime.timedelta(1 * 365 / 12)
            elif m == "3":
                break

            year_now = datetime.datetime.date(a).strftime("%Y")
            month_now = datetime.datetime.date(a).strftime("%m")
            day_now = datetime.datetime.date(a).strftime("%d")
            c = calendar.TextCalendar(calendar.MONDAY)
            year_input, month_input, day_input = int(
                year_now), int(month_now), int(day_now)
            calendar_month = c.formatmonth(
                year_input, month_input, day_input, 0)
            print(calendar_month)
            self.select_slots(appointmentNo)

    def cancel_appointment(self, appointmentNo):
        print("Do you confirm that you want to cancel this appointment?")
        while True:
            a = input('1. Yes \n2. No\nYou choose number: ')
            if a == "1":
                appointmentNo = int(appointmentNo)
                Database().delete_appointment(appointmentNo)
                print("You have successfully cancelled this appointment")
                break
            elif a == "2":
                break
            else:
                print("\nPlease input 1 or 2.\n")
                year_now = datetime.datetime.date(a).strftime("%Y")
                month_now = datetime.datetime.date(a).strftime("%m")
                day_now = datetime.datetime.date(a).strftime("%d")
                c = calendar.TextCalendar(calendar.MONDAY)
                year_input, month_input, day_input = int(
                    year_now), int(month_now), int(day_now)
                calendar_month = c.formatmonth(
                    year_input, month_input, day_input, 0)
                print(calendar_month)
                self.select_slots(appointmentNo)

    def select_slots(self, appointmentNo):
        while True:
            select_date = input(
                "Please enter a valid date in YYYY-MM-DD format between now and the close of the month: ")

            db = Database()
            db.exec_one("""SELECT substr(s.startTime, 12, 2), s.slot_id, u.firstName, u.lastName, u.userId as gp_id, row_number() OVER (PARTITION by s.slot_id order by random()) as rand_order
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
            result = db.c.fetchall()
            rows = []
            for i in result:
                rows.append(list(i))

            available_session = {}
            for i in rows:
                if i[0] in available_session:
                    available_session[i[0]].append(i[4])
                else:
                    available_session[i[0]] = [i[4]]
            # print()
            print("Please select an appointment time:")
            sessions = ["09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00",
                        "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00"]
            num = 1
            for i in sessions:
                if i[:2] in list(available_session.keys()):
                    print(str(num) + ". "+i)
                    num += 1
            print(str(num) + ". Back")
            booked_slot = int(input("Enter your option : "))

            if booked_slot == num:
                break
            elif booked_slot in range(9):
                # Assign GP6 to this appointment temporarily.
                # selected_session = available_session[booked_slot - 1][:2]
                slot, gp = rows[booked_slot-1][1], rows[booked_slot-1][-2]
                a = [(self.patient_id, slot, gp), ]

                db.exec_many(
                    "INSERT INTO Appointment(patient_id,slot_id,gp_id) Values (?,?,?)", a)
                db.exec(
                    "DELETE FROM Appointment WHERE appointment_id = " + str(appointmentNo))
                print("SUCCESS - "
                      "You have successfully requested an appointments with one of our GP's, \n"
                      " You will be alerted once your appointment is confirmed")
                break

        def view_prescription(self):
            print("Patient id: " + str(self.patient_id) +
                  "want to view prescription\n")
            return


if __name__ == "__main__":
    Patient(4).select_options()
