import sqlite3


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Database:
    def __init__(self):
        self.connection = sqlite3.connect('database/ehealth.db')
        self.connection.row_factory = dict_factory
        self.c = self.connection.cursor()
        #     run db build on initialisation
        self.build_script = open('ehealth.db.sql', "r").read()
        self.c.executescript(self.build_script)

    def email_list(self):
        self.c.execute("SELECT email FROM Users")
        email_list = []
        for i in self.c.fetchall():
            email_list.append(i['email'])
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

    def close_db(self):
        self.c.close()
        self.connection.close()
