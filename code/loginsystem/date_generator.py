import datetime
import calendar
import operator

years = [2021, 2022, 2023, 2024, 2025]
months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
months_list = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

dates_list = [datetime.datetime.strptime(i, "%m").date().month for i in months_list]

days_dt = []
close_dt = []
years_dt = []
months_dt = []

for year in years:
    for i in dates_list:
        days_dt.append(i)

for year in years:
    for i in months:
        close_dt.append(calendar.monthrange(year, i))

for date in close_dt:
    years_dt.append(str(date[1]))

for year in years:
    for i in months:
        months_dt.append(year)

last_days = [str(n) + "-" + str(o) + "-" + m for m, n, o in zip(years_dt, months_dt, days_dt)]

last_days_dt = [datetime.datetime.strptime(i, '%Y-%m-%d').date() for i in last_days]


def date_sort(dater):
    global ld_nm
    index_length = range(0, len(last_days_dt))
    value_to_sort = datetime.datetime.strptime(dater, '%Y-%m-%d').date()
    for i in index_length:
        while last_days_dt[i-1] < value_to_sort and i > 0:
            ld_nm = operator.itemgetter(i+1)(last_days_dt)
            i = i+1
    return ld_nm


print(date_sort("2023-01-22"))

global ld_nm
