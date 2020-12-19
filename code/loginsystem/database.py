import sqlite3


class Database:
    def __init__(self):
        self.connection = sqlite3.connect('../../database/ehealth.db')
        self.c = self.connection.cursor()

    def patient_email_list(self):
        self.c.execute("SELECT email FROM Patients")
        email_list = []
        for i in self.c.fetchall():
            email_list.append(i[0])
        return email_list

    def exec_many(self, query, obj):
        self.c.executemany(query, obj)
        self.connection.commit()

    def exec_one(self, query, obj):
        self.c.execute(query, obj)
        self.connection.commit()

    def exec(self, query):
        self.c.execute(query)
        self.connection.commit()
