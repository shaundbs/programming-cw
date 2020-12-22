from datetime import datetime


# class Validation:
#
#     def date_validation(self, date):
#         try:
#             datetime.strptime(date, '%m/%d/%Y')
#             print('The date {} is valid.'.format(date))
#         except ValueError:
#             print('The date {} is invalid'.format(date))

inp = input('enter a number...')
try:  # checks if input is numeric, i.e. 2, 39, 4592 etc
    inp = int(inp)
except(ValueError):  # Was not numeric, i.e. was a letter, word or some character
    try:
        inp = float(inp)  # Let's try again, could be user entered 3.5 or some other float value.
    except(ValueError):
        print("OK forget it")