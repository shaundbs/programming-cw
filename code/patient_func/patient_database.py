import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sqlite3


class Database:

    def patient_email_list(self):
        self.connection = sqlite3.connect('../../database/ehealth.db')
        self.c = self.connection.cursor()
        self.c.execute("SELECT email FROM Users")
        email_list = []
        for i in self.c.fetchall():
            email_list.append(i[0])
        self.connection.close()
        return email_list

    def delete_appointment(self, appointmentNo):
        self.connection = sqlite3.connect('../../database/ehealth.db')
        self.c = self.connection.cursor()
        a = [(appointmentNo), ]
        self.c.execute(
            "DELETE FROM Appointment WHERE appointment_id = ?", a)
        self.connection.commit()
        self.connection.close()

    def exec_many(self, query, obj):
        self.connection = sqlite3.connect('../../database/ehealth.db')
        self.c = self.connection.cursor()
        self.c.executemany(query, obj)
        self.connection.commit()

    def exec_one(self, query, obj):
        self.connection = sqlite3.connect('../../database/ehealth.db')
        self.c = self.connection.cursor()
        self.c.execute(query, obj)
        self.connection.commit()

    def exec(self, query):
        self.connection = sqlite3.connect('../../database/ehealth.db')
        self.c = self.connection.cursor()
        self.c.execute(query)
        self.connection.commit()

    def reschedule(self, request, appointmentNo):
        self.connection = sqlite3.connect('../../database/ehealth.db')
        self.c = self.connection.cursor()
        self.c.execute(
            "INSERT INTO Appointment(patient_id,slot_id,gp_id,reason) Values (?,?,?,?)", request)
        self.c.execute(
            "DELETE FROM Appointment WHERE appointment_id = " + str(appointmentNo))
        self.connection.commit()

    def gp_name(self, id):
        self.connection = sqlite3.connect('../../database/ehealth.db')
        self.c = self.connection.cursor()
        self.c.execute(
            "SELECT firstName, lastName FROM Users WHERE userId = ?", (id,))
        result = self.c.fetchone()
        return list(result)
