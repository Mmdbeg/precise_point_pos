import os
from flask import Blueprint, request, render_template
import datetime as dt
import re
import subprocess
import urllib.request

upload_rinex = Blueprint("upload_rinex", __name__)

# these functions extract dd mm yy from rinex file name -+-+-+---+-+-+-+-+-++-+-+-+-+-++-+-+-+-+-++-+-+-+-+-++-+-+-+-+-++-+-+-+-+-+
def extract_month(filename):
    match = re.search(r'[a-zA-Z]+(\d{2})(\d{2})\.\d{2}o$', filename)
    return match.group(1) if match else None

def extract_day(filename):
    match = re.search(r'[a-zA-Z]+(\d{2})(\d{2})\.\d{2}o$', filename)
    return match.group(2) if match else None

def extract_year(filename):
    match = re.search(r'\.(\d{2})o$', filename)
    return match.group(1) if match else None
#-+-+-+---+-+-+-+-+-++-+-+-+-+-++-+-+-+-+-++-+-+-+-+-++-+-+-+-+-++-+-+-+-+-+-+-+-+---+-+-+-+-+-++-+-+-+-+-++-+-+-+-+-++-+-+-+-+-++-+-+-

# this function can calculate gps day (use it to down load precise ephemerieds and clock correction)+-++-+-+-+-+--+-+--+-+-+-+-+-+-+-+-+-+
def gps_week_and_day(date):
    """Calculate GPS week number and day of the week for a given date."""
    gps_start_epoch = dt.datetime(1980, 1, 6)
    delta_days = (date - gps_start_epoch).days  # Convert timedelta to integer days
    gps_week, gps_day = divmod(delta_days, 7)  # Compute week and day
    return gps_week, gps_day



@upload_rinex.route("/", methods=["GET", "POST"])
def upload_ri():
    success_message = None
    error_message = None

    if request.method == "POST":
        if "file" not in request.files:
            error_message = "⚠️ No file part in the request!"
            return render_template("home.html", error_message=error_message)

        file = request.files["file"]
        if file.filename == "":
            error_message = "⚠️ No file selected!"
            return render_template("home.html", error_message=error_message)

        # Create a subfolder named after the file (without extension)
        upload_folder = "uploads"
        file_basename = os.path.splitext(file.filename)[0]  # Removes extension
        subfolder_path = os.path.join(upload_folder, file_basename)
        
        # Create the subfolder if it doesn't exist
        os.makedirs(subfolder_path, exist_ok=True)

        # Save the file inside the subfolder
        file_path = os.path.join(subfolder_path, file.filename)
        file.save(file_path)

        # Extract date info (your existing logic)
        extracted_day = extract_day(file.filename)
        extracted_month = extract_month(file.filename)
        extracted_year = extract_year(file.filename)

        if all([extracted_day, extracted_month, extracted_year]):
            full_date = dt.datetime(int("20" + extracted_year), int(extracted_month), int(extracted_day))
            gps_week, gps_day = gps_week_and_day(full_date)
            success_message = (
                f"✅ File uploaded successfully .the observe Date: {extracted_day}/{extracted_month}/20{extracted_year}. "
                f"GPS Week: {gps_week}, Day: {gps_day}."
            )
        else:
            success_message = f"✅ File uploaded to folder '{file_basename}'! (Date not extracted)"



    return render_template("home.html", success_message=success_message, error_message=error_message)