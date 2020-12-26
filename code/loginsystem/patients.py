import sqlite3
# hide password when inputting
from database import Database
import re
import datetime as datetime
import getpass
import bcrypt
import calendar
from tabulate import tabulate
from termcolor import colored
from pandas import DataFrame


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
            print("1. Book an appointment this month \n"
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
                        select_date = input(
                            "Please enter a valid date in YYYY-MM-DD format between now and the close of next month:\n")
                        fm_date = datetime.datetime.strptime(
                            select_date, '%Y-%m-%d').date()
                        try:
                            if datetime.datetime.now().date() < datetime.datetime.strptime(select_date,
                                                                                           '%Y-%m-%d').date() \
                                    < datetime.datetime.now().date() + one_month:
                                datetime.datetime.strptime(
                                    select_date, '%Y-%m-%d')

                                print('The date {} is valid.'.format(select_date))

                                index_1 = ["startTime", "endTime", "slot_id", "firstName", "lastName", "gp_id",
                                           "rand_order"]
                                db = Database()

                                db.exec_one(
                                    "SELECT s.startTime, s.endTime, s.slot_id, u.firstName, u.lastName, u.userId "
                                    "as gp_id, row_number() "
                                    "OVER(PARTITION by s.slot_id order by random()) as rand_order "
                                    "FROM SLOTS S "
                                    "CROSS JOIN Users U "
                                    "LEFT JOIN APPOINTMENT A "
                                    "ON S.slot_id = A.slot_id "
                                    "AND A.gp_id = U.userId "
                                    "AND((A.IS_CONFIRMED =0 AND A.IS_REJECTED=0) OR(A.is_confirmed = 1)) "
                                    # EITHER UNCONFIRMED/UNREJECTED OR CONFIRMED we wil remove.
                                    "LEFT JOIN gp_time_off gpto "  # IF SLOT FALLS BETWEEN START AND ENDTIME
                                    # OF GP TIME OFF WE WILL REMOVE
                                    " ON datetime(S.startTime) >= datetime(GPTO.startTime) AND "
                                    "datetime(s.startTime) < datetime(GPTO.endTime) "
                                    "AND GPTO.gp_id = U.userId "
                                    "WHERE U.accountType = 'gp' "  # GP
                                    "and "
                                    "u.is_active = 1 "  # active GP
                                    # limit to date we looking for
                                    "AND DATE(S.startTime) = DATE(?) "
                                    "AND A.GP_ID IS NULL "  # remove gps with appts
                                    "AND GPTO.GP_ID IS NULL", (fm_date,))  # remove anyone with time off schedule over that appt time

                                result = db.c.fetchall()
                                df1 = DataFrame(result)
                                df1.columns = index_1

                                print(colored('Available Appointments \n',
                                              'green', attrs=['bold']))
                                print(tabulate(df1, headers='keys',
                                               tablefmt='fancy_grid', showindex=False))

                                print("Please select an appointment time: \n")
                                print("1. 09:00-10:00")
                                print("2. 10:00-11:00")
                                print("3. 11:00-12:00")
                                print("4. 12:00-13:00")
                                print("5. 13:00-14:00")
                                print("6. 14:00-15:00")
                                print("7. 15:00-16:00")
                                print("8. 16:00-17:00")
                                booked_slot = int(
                                    input("Enter your option : "))
                                print(booked_slot)
                                a = [(self.patient_id, booked_slot,), ]
                                db.exec_many(
                                    "INSERT INTO Appointment(patient_id,slot_id) Values (?,?)", a)
                                print("SUCCESS - You have successfully requested an appointment "
                                      "with one of our GP's,\n"
                                      " You will be alerted once your appointment is confirmed")
                                if 1 <= booked_slot <= 8:
                                    print(
                                        "SUCCESS - You have successfully requested an appointment"
                                        " with one of our GP's,\n"
                                        " You will be alerted once your appointment is confirmed")
                                    break
                                else:
                                    print(
                                        "This value is not accepted please enter a number between 1-8")
                                continue
                            else:
                                print("Please select a valid date")
                                continue
                        except ValueError:
                            print(
                                "This value is not accepted. Please enter a date in YYYY-MM-DD format:")
                except ValueError:
                    print("No idea")
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
                db = Database()
                try:
                    while True:
                        select_date = input(
                            "Please enter a valid date in YYYY-MM-DD format between now and the close of the month: ")
                        fm_date = datetime.datetime.strptime(
                            select_date, '%Y-%m-%d').date()
                        try:
                            if datetime.datetime.now().date() < datetime.datetime.strptime(select_date, '%Y-%m-%d').date() \
                                    < datetime.datetime.now().date() + one_month:
                                datetime.datetime.strptime(
                                    select_date, '%Y-%m-%d')
                                print('The date {} is valid.'.format(select_date))

                                index_1 = ["startTime", "endTime", "slot_id", "firstName", "lastName", "gp_id",
                                           "rand_order"]
                                db = Database()

                                db.exec_one(
                                    "SELECT s.startTime, s.endTime, s.slot_id, u.firstName, u.lastName, u.userId "
                                    "as gp_id, row_number() "
                                    "OVER(PARTITION by s.slot_id order by random()) as rand_order "
                                    "FROM SLOTS S "
                                    "CROSS JOIN Users U "
                                    "LEFT JOIN APPOINTMENT A "
                                    "ON S.slot_id = A.slot_id "
                                    "AND A.gp_id = U.userId "
                                    "AND((A.IS_CONFIRMED =0 AND A.IS_REJECTED=0) OR(A.is_confirmed = 1)) "
                                    # EITHER UNCONFIRMED/UNREJECTED OR CONFIRMED we wil remove.
                                    "LEFT JOIN gp_time_off gpto "  # IF SLOT FALLS BETWEEN START AND ENDTIME
                                    # OF GP TIME OFF WE WILL REMOVE
                                    " ON datetime(S.startTime) >= datetime(GPTO.startTime) AND "
                                    "datetime(s.startTime) < datetime(GPTO.endTime) "
                                    "AND GPTO.gp_id = U.userId "
                                    "WHERE U.accountType = 'gp' "  # GP
                                    "and "
                                    "u.is_active = 1 "  # active GP
                                    # limit to date we looking for
                                    "AND DATE(S.startTime) = DATE(?) "
                                    "AND A.GP_ID IS NULL "  # remove gps with appts
                                    "AND GPTO.GP_ID IS NULL",
                                    (fm_date,))  # remove anyone with time off schedule over that appt time

                                result = db.c.fetchall()
                                df1 = DataFrame(result)
                                df1.columns = index_1

                                print(colored('Available Appointments',
                                              'green', attrs=['bold']))
                                print(tabulate(df1, headers='keys',
                                               tablefmt='fancy_grid', showindex=False))

                                print("Please select an appointment time: ")
                                print("1. 09:00-10:00")
                                print("2. 10:00-11:00")
                                print("3. 11:00-12:00")
                                print("4. 12:00-13:00")
                                print("5. 13:00-14:00")
                                print("6. 14:00-15:00")
                                print("7. 15:00-16:00")
                                print("8. 16:00-17:00")
                                booked_slot = int(
                                    input("Enter your option : "))
                                print(booked_slot)
                                if 1 <= booked_slot <= 8:
                                    print(
                                        "SUCCESS - You have successfully requested an appointments with one of our GP's, \n"
                                        " You will be alerted once your appointment is confirmed")
                                    a = [
                                        (self.patient_id, booked_slot, select_date,), ]
                                    db.exec_many(
                                        "INSERT INTO Appointment(patient_id,slot_id,date) Values (?,?,?)", a)
                                    print("SUCCESS - "
                                          "You have successfully requested an appointments with one of our GP's, \n"
                                          " You will be alerted once your appointment is confirmed")
                                    break
                                else:
                                    print(
                                        "This value is not accepted please enter a number between 1-8")
                                continue
                            else:
                                print(
                                    "Please select a valid date (from today up until the end of next month)")
                                continue
                        except ValueError:
                            print(
                                "This value is not accepted. Please enter a date in YYYY-MM-DD format:")
                except ValueError:
                    print("Not accepted")
            elif menu_choice == '3':
                break
            else:
                print('Wrong input. Please try again.')

# else:
#     print('Wrong input. Please try again.')

# clean up and improve error messages
# fix timeslot loop so that it goes back to the timeslots instead of calendar

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
