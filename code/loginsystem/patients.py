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

    def select_options(self):
        print('1. Request Appointments')
        print('2. View Appointments')
        print('3. View Prescription')
        print('4. Log out')
        option = input('Please choose an option: ')
        return option

    def request_time(self):
        time_now = datetime.datetime.now()
        year_now = datetime.datetime.date(time_now).strftime("%Y")
        month_now = datetime.datetime.date(time_now).strftime("%m")
        day_now = datetime.datetime.date(time_now).strftime("%d")
        c = calendar.TextCalendar(calendar.MONDAY)
        year_input, month_input, day_input = int(year_now), int(month_now), int(day_now)
        calendar_month = c.formatmonth(year_input, month_input, day_input, 0)
        print(calendar_month)
        select_date = int(input("Please enter a day: "))
        print(select_date)
        print("Please select an appointment time: ")
        print("1. 09:00-10:00")
        print("2. 10:00-11:00")
        print("3. 11:00-12:00")
        print("4. 12:00-13:00")
        print("5. 13:00-14:00")
        print("6. 14:00-15:00")
        print("7. 15:00-16:00")
        print("8. 16:00-17:00")
        booked_slot = input("Enter your option : ")
        return booked_slot


    # print array of time slots

    # if 1 <= select_date <= 31:
    #     start_time = '9:00'
    #     end_time = '17:00'
    #     slot_time = 60
    #
    #     # Start date from today to next 5 day
    #     start_date = datetime.datetime.now().date()
    #     end_date = datetime.datetime.now().date() + datetime.timedelta(days=0)
    #     days = []
    #     date = start_date
    #     while date <= end_date:
    #         hours = []
    #         time = datetime.datetime.strptime(start_time, '%H:%M')
    #         end = datetime.datetime.strptime(end_time, '%H:%M')
    #         while time <= end:
    #             hours.append(time.strftime("%H:%M"))
    #             time += datetime.timedelta(minutes=slot_time)
    #         date += datetime.timedelta(days=1)
    #         days.append(hours)
    #
    #     for hours in days:
    #         print(hours)


    # def request_appointment(self):
    #     if booked_slot == '1':
    #         print("Well done Shaun!")
    #     else:
    #         print("You flopped!!")
        # elif privilege == '2':
        #     a.view_appointment()
        # elif privilege == '3':
        #     a.view_prescription()
        # elif privilege == '4':
        #     break
        # # display calendar for patients from the date of login session
        # db = Database()
        # s_time =
        # e_time =
        # a = [(s_time, e_time,), ]
        # db.exec_many(
        # "INSERT INTO Slots(startTime,endTime) Values (?,?)", a)


def view_appointment(self):
    a = [(self.patient_id), ]
    db = Database()
    db.exec_one("SELECT * FROM Appointment WHERE patient_Id = ?", a)
    result = db.c.fetchall()
    for i in result:
        print(i)


def view_prescription(self):
    print("Patient id: " + str(self.patient_id) +
          "want to view prescription\n")
    return
