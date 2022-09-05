import time
import datetime

date_string = "4/9/2022"

time_tokens = date_string.split('/')
day = int(time_tokens[0])
month = int(time_tokens[1])
year = int(time_tokens[2])
dt = datetime.datetime(year=year, month=month, day=day)
time_float = time.mktime(dt.timetuple())
print(f"{year}-{month}-{day}")
print(time_float)