import datetime
from dateutil.relativedelta import relativedelta
from loginsystem import database as db


def db_gen_slots():
    # populate one month of slots table.
    date = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    end_date = date + relativedelta(months=1)
    start_hour = 9
    end_hour = 17

    start_slot = date

    slots = []

    while start_slot <= end_date:

        start_slot += relativedelta(hours=start_hour)  # set to 9am
        slot_time = int(start_slot.strftime("%H"))
        while slot_time < end_hour:
            slots.append([start_slot.strftime("%Y-%m-%d %H:%M:00"),
                          (start_slot + relativedelta(hours=1)).strftime("%Y-%m-%d %H:%M:00")])
            slot_time += 1
            start_slot += relativedelta(hours=1)
        start_slot += relativedelta(days=1)
        start_slot -= relativedelta(hours=end_hour)

    # conn = db.Database()

    for time in slots:
        #     conn.exec("INSERT INTO SLOT(STARTTIME, ENDTIME) VALUES ('{time[0]}', '{time[1]}')")
        print(f"INSERT INTO SLOTS(STARTTIME, ENDTIME) VALUES ('{time[0]}', '{time[1]}');")


# db_gen_slots()


def password_checker(password):
    # Not being put into use now.
    length_error = len(password) < 8
    # searching for digits
    digit_error = re.search(r"\d", password) is None
    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None
    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None
    # searching for symbols
    symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None
    # overall result
    password_ok = not (length_error or digit_error or uppercase_error or lowercase_error or symbol_error)
    return {
        'password_ok': password_ok,
        'length_error': length_error,
        'digit_error': digit_error,
        'uppercase_error': uppercase_error,
        'lowercase_error': lowercase_error,
        'symbol_error': symbol_error,
    }