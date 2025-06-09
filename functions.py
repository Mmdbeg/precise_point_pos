import datetime as dt
import os
import subprocess
import re
import requests

# --- time convertor --- 
def gps_week_and_day(date):
    """Calculate GPS week number and day of the week for a given date."""
    gps_start_epoch = dt.datetime(1980, 1, 6)
    delta_days = (date - gps_start_epoch).days  # Convert timedelta to integer days
    gps_week, gps_day = divmod(delta_days, 7)  # Compute week and day
    return gps_week, gps_day

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

# --- Decompress .Z files using gzip ---
def decompress_z_file(z_path):
    try:
        subprocess.run(['gzip', '-df', z_path], check=True)
        print(f"Decompressed: {z_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to decompress {z_path}: {e}")

# ---  making a list of files name ---
def generate_igr_filenames(gps_week, gps_day, days):
    sp3_filenames = []
    clk_filenames = []

    for i in range(days):
        total_day = gps_day + i
        current_week = gps_week + total_day // 7
        current_day = total_day % 7

        sp3_filename = f"igr{current_week}{current_day}.sp3"
        clk_filename = f"igr{current_week}{current_day}.clk"

        sp3_filenames.append(sp3_filename)
        clk_filenames.append(clk_filename)
    
    return sp3_filenames + clk_filenames

# --- Download SP3 and CLK files ---
def downloader(gps_week, gps_day, days, folder_path):
    os.makedirs(folder_path, exist_ok=True)
    for i in range(days):
        total_day = gps_day + i
        current_week = gps_week + total_day // 7
        current_day = total_day % 7

        sp3_filename = f"igr{current_week}{current_day}.sp3.Z"
        clk_filename = f"igr{current_week}{current_day}.clk.Z"

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

def parse_sum_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Extract section 3.3 Coordinate estimates
    coord_estimate_pattern = r"3\.3 Coordinate estimates(.*?)3\.4 Coordinate differences"
    coord_diff_pattern = r"3\.4 Coordinate differences ITRF \(IGS05\)(.*?)(?:\n\n|\Z)"

    estimate_match = re.search(coord_estimate_pattern, content, re.DOTALL)
    diff_match = re.search(coord_diff_pattern, content, re.DOTALL)

    estimate_text = estimate_match.group(1).strip() if estimate_match else "No Coordinate estimates found."
    diff_text = diff_match.group(1).strip() if diff_match else "No Coordinate differences found."

    # Optionally, you can do more structured parsing here (e.g. into dicts) if you want nicer formatting.

    # For now, return plain text
    return estimate_text, diff_text
