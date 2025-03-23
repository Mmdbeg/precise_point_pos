import datetime as dt
import sys
import matplotlib.pyplot as plt 
import numpy 
import flask

def gps_week_and_day(date):
    """Calculate GPS week number and day of the week for a given date."""
    gps_start_epoch = dt.datetime(1980, 1, 6)
    delta_days = (date - gps_start_epoch).days  # Convert timedelta to integer days
    gps_week, gps_day = divmod(delta_days, 7)  # Compute week and day
    return gps_week, gps_day

# Read input arguments from Bash script
d = int(sys.argv[1])
m = int(sys.argv[2])
y = int(sys.argv[3])

# Convert input to datetime object
x = dt.datetime(y, m, d)

# Get GPS week and day
gps_week, gps_day = gps_week_and_day(x)

#  FIX: Print output in the correct format
print("GPS Week:", gps_week)
print("Day:", gps_day)


