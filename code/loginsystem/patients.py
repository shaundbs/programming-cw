import sqlite3
# hide password when inputting
from database import Database
import re
import datetime as datetime
import getpass
import bcrypt
import calendar


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
        date_time = time_now.strftime("%m/%d/%Y %H:%M:%S")
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
                year_input, month_input, day_input = int(year_nm), int(month_nm), int(day_nm)
                calendar_month = c.formatmonth(year_input, month_input, day_input, 0)
                print(calendar_month)
                db = Database()
                try:
                    while True:
                        select_date = input(
                            "Please enter a valid date in YYYY-MM-DD format between now and the close of next month: \n")
                        try:
                            if datetime.datetime.now().date() < datetime.datetime.strptime(select_date, '%Y-%m-%d').date() \
                                    < datetime.datetime.now().date() + one_month:
                                datetime.datetime.strptime(select_date, '%Y-%m-%d')
                                print('The date {} is valid.'.format(select_date))
                                print("Please select an appointment time: ")
                                print("1. 09:00-10:00")
                                print("2. 10:00-11:00")
                                print("3. 11:00-12:00")
                                print("4. 12:00-13:00")
                                print("5. 13:00-14:00")
                                print("6. 14:00-15:00")
                                print("7. 15:00-16:00")
                                print("8. 16:00-17:00")
                                booked_slot = int(input("Enter your option : "))
                                print(booked_slot)
                                a = [(self.patient_id, booked_slot, select_date,), ]
                                db.exec_many(
                                    "INSERT INTO Appointment(patient_id,slot_id,date) Values (?,?,?)", a)
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
                                    print("This value is not accepted please enter a number between 1-8")
                                continue
                            else:
                                print("Please select a valid date")
                                continue
                        except ValueError:
                            print("This value is not accepted. Please enter a date in YYYY-MM-DD format:")
                except ValueError:
                    print("No idea")
            elif menu_choice == '1':
                time_now = datetime.datetime.now()
                year_now = datetime.datetime.date(time_now).strftime("%Y")
                month_now = datetime.datetime.date(time_now).strftime("%m")
                day_now = datetime.datetime.date(time_now).strftime("%d")
                one_month = datetime.timedelta(1 * 365 / 12)
                c = calendar.TextCalendar(calendar.MONDAY)
                year_input, month_input, day_input = int(year_now), int(month_now), int(day_now)
                calendar_month = c.formatmonth(year_input, month_input, day_input, 0)
                print(calendar_month)
                db = Database()
                try:
                    while True:
                        select_date = input(
                            "Please enter a valid date in YYYY-MM-DD format between now and the close of the month: ")
                        try:
                            if datetime.datetime.now().date() < datetime.datetime.strptime(select_date, '%Y-%m-%d').date() \
                                    < datetime.datetime.now().date() + one_month:
                                datetime.datetime.strptime(select_date, '%Y-%m-%d')
                                print('The date {} is valid.'.format(select_date))
                                print("Please select an appointment time: ")
                                print("1. 09:00-10:00")
                                print("2. 10:00-11:00")
                                print("3. 11:00-12:00")
                                print("4. 12:00-13:00")
                                print("5. 13:00-14:00")
                                print("6. 14:00-15:00")
                                print("7. 15:00-16:00")
                                print("8. 16:00-17:00")
                                booked_slot = int(input("Enter your option : "))
                                print(booked_slot)
                                if 1 <= booked_slot <= 8:
                                    print(
                                        "SUCCESS - You have successfully requested an appointments with one of our GP's, \n"
                                        " You will be alerted once your appointment is confirmed")
                                    a = [(self.patient_id, booked_slot, select_date,), ]
                                    db.exec_many(
                                        "INSERT INTO Appointment(patient_id,slot_id,date) Values (?,?,?)", a)
                                    print("SUCCESS - "
                                          "You have successfully requested an appointments with one of our GP's, \n"
                                          " You will be alerted once your appointment is confirmed")
                                    break
                                else:
                                    print("This value is not accepted please enter a number between 1-8")
                                continue
                            else:
                                print("Please select a valid date (from today up until the end of next month)")
                                continue
                        except ValueError:
                            print("This value is not accepted. Please enter a date in YYYY-MM-DD format:")
                except ValueError:
                    print("Not accepted")
            elif menu_choice == '3':
                break
            else:
                print('Wrong input. Please try again.')



        # else:
        #     print('Wrong input. Please try again.')

        # improve this by making options subjective by month and adding gp conditional booking
        # weekend/bank holiday conditionals
        # clean up and improve error messages
        # fix timeslot loop so that it goes back to the timeslots instead of calendar

    def confirm_appointment(self):
        if self.request_time() == '1':
            print("Well done Shaun, you have successfully booked an appointment!")
        else:
            print("Failure")

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
                elif i[-2] == 0:
                    status = "confirmed."
                else:
                    status = "rejected."
                print(str(num) + ". Your appointment with Dr " +
                      str(i[1]) + " " + str(i[2]) + " at " + str(i[3][:8]) + " is " + status)
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
                "\nThis appointment is confired.\n1. Reschedule this appointment.\n2. Cancel this appointment.\n3. Back")
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
        pass

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

    def view_prescription(self):
        print("Patient id: " + str(self.patient_id) +
              "want to view prescription\n")
        return
