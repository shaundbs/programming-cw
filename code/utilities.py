import datetime
from dateutil.relativedelta import relativedelta

def db_gen_slots():
    # populate one month of slots table.
    date = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    end_date = date + relativedelta(months=1)

    print(date, end_date)

    start_slot = date

    slots = []


    while start_slot <= end_date:
        start_slot += relativedelta(hours=9) # set to 9am
        slot_time= int(start_slot.strftime("%H"))
        while slot_time < 17:
            slots.append(start_slot.strftime("%Y-%m-%d %H:%M:00"))
            slot_time += 1
            start_slot += relativedelta(hours=1)
        # start_slot=start_slot.replace(hour=0)






print(db_gen_slots())