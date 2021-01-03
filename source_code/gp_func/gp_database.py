import sqlite3

"""
Same as loginsystem db except with dictionary support to return results in an easier format to work with."""


def dict_factory(cursor,
                 row):  # return results as dictionaries https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.row_factory
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Database:
    def __init__(self):
        self.connection = sqlite3.connect('../database/ehealth.db')
        self.connection.row_factory = dict_factory  # return results as dictionaries https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.row_factory
        self.c = self.connection.cursor()
        #     run db build on initialisation
        self.build_script = open('../ehealth.db.sql', "r").read()
        self.c.executescript(self.build_script)

    def patient_email_list(self):
        self.c.execute("SELECT email FROM Users")
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

    def fetch_data(self, query_string):
        self.c.execute(query_string)
        data = self.c.fetchall()
        return data
