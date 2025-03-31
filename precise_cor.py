import georinex as gr
import pandas as pd
import sys
import re


if len(sys.argv) < 2:
    print("Error: No file path provided!")
    sys.exit(1)  # Exit to prevent further execution

file_path = sys.argv[1]  # Receiving file name from Bash script
print(f"Processing file: {file_path}")


# Class to handle RINEX observation file
class RinexObs:
    def __init__(self, file_path,obs_day):
        self.ri_path = file_path
        self.data = gr.load(file_path)      
        self.start_time = pd.to_datetime(self.data.time[0].values)
        self.end_time = pd.to_datetime(self.data.time[-1].values)
  

    def __str__(self):
        return f"RINEX File: {self.ri_path}\nStart Time: {self.start_time}\nEnd Time: {self.end_time}"

