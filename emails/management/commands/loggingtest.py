import datetime

test_var = 'test log text'

file = open(r'C:\Users\timmu\Documents\Coding Projects\email_processor\emails\management\commands\loggingtest.txt', 'a')
file.write(f'{datetime.datetime.now()} - {test_var} \n')