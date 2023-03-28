import datetime
file = open(r'C:\Users\timmu\Documents\Coding Projects\email_processor\testscript.txt', 'a')

file.write(f'{datetime.datetime.now()} - The script ran \n')