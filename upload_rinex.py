import os
from flask import Blueprint, request, render_template
import datetime as dt
import re
import requests
import subprocess

upload_rinex = Blueprint("upload_rinex", __name__)

# --- Extract date info from RINEX filename ---
def extract_month(filename):
    match = re.search(r'[a-zA-Z]+(\d{2})(\d{2})\.\d{2}o$', filename)
    return match.group(1) if match else None

def extract_day(filename):
    match = re.search(r'[a-zA-Z]+(\d{2})(\d{2})\.\d{2}o$', filename)
    return match.group(2) if match else None

def extract_year(filename):
    match = re.search(r'\.(\d{2})o$', filename)
    return match.group(1) if match else None

# --- Convert date to GPS week/day ---
def gps_week_and_day(date):
    gps_start_epoch = dt.datetime(1980, 1, 6)
    delta_days = (date - gps_start_epoch).days
    gps_week, gps_day = divmod(delta_days, 7)
    return gps_week, gps_day

# --- Decompress .Z files using gzip ---
def decompress_z_file(z_path):
    try:
        subprocess.run(['gzip', '-df', z_path], check=True)
        print(f"Decompressed: {z_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to decompress {z_path}: {e}")

# --- Download SP3 and CLK files ---
def downloader(gps_week, gps_day, days, folder_path):
    os.makedirs(folder_path, exist_ok=True)
    for i in range(days):
        day = gps_day + i
        sp3_filename = f"igr{gps_week}{day}.sp3.Z"
        clk_filename = f"igr{gps_week}{day}.clk.Z"

        sp3_url = f"https://cddis.nasa.gov/archive/gnss/products/{gps_week}/{sp3_filename}"
        clk_url = f"https://cddis.nasa.gov/archive/gnss/products/{gps_week}/{clk_filename}"

        sp3_path = os.path.join(folder_path, sp3_filename)
        clk_path = os.path.join(folder_path, clk_filename)

        try:
            sp3_response = requests.get(sp3_url)
            sp3_response.raise_for_status()
            with open(sp3_path, "wb") as f:
                f.write(sp3_response.content)
            print(f"✅ SP3 downloaded: {sp3_filename}")
        except requests.HTTPError as e:
            print(f"❌ SP3 download failed: {e}")

        try:
            clk_response = requests.get(clk_url)
            clk_response.raise_for_status()
            with open(clk_path, "wb") as f:
                f.write(clk_response.content)
            print(f"✅ CLK downloaded: {clk_filename}")
        except requests.HTTPError as e:
            print(f"❌ CLK download failed: {e}")

        # Decompress
        decompress_z_file(sp3_path)
        decompress_z_file(clk_path)

# --- Main Flask route ---
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

        # Create subfolder
        upload_folder = "uploads"
        file_basename = os.path.splitext(file.filename)[0]
        subfolder_path = os.path.join(upload_folder, file_basename)
        os.makedirs(subfolder_path, exist_ok=True)

        # Save file
        file_path = os.path.join(subfolder_path, file.filename)
        file.save(file_path)

        # Extract date from filename
        extracted_day = extract_day(file.filename)
        extracted_month = extract_month(file.filename)
        extracted_year = extract_year(file.filename)

        if all([extracted_day, extracted_month, extracted_year]):
            full_date = dt.datetime(int("20" + extracted_year), int(extracted_month), int(extracted_day))
            gps_week, gps_day = gps_week_and_day(full_date)

            # Download and decompress .sp3.Z and .clk.Z files
            downloader(gps_week, gps_day, 2, subfolder_path)

            success_message = (
                f"✅ File uploaded successfully! Observation Date: {extracted_day}/"
                f"{extracted_month}/20{extracted_year}. GPS Week: {gps_week}, Day: {gps_day}."
            )
        else:
            success_message = f"✅ File uploaded to folder '{file_basename}'! (Date not extracted)"

    return render_template("home.html", success_message=success_message, error_message=error_message)
