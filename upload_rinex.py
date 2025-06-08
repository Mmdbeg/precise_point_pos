import os
from flask import Blueprint, request, render_template
import datetime as dt
import re
import requests
import subprocess
import shutil
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

# ---  making a list of files name ---
def generate_igr_filenames(gps_week, gps_day, days):
    filenames = []
    for i in range(days):
        total_day = gps_day + i
        current_week = gps_week + total_day // 7
        current_day = total_day % 7

        sp3_filename = f"igr{current_week}{current_day}.sp3"
        clk_filename = f"igr{current_week}{current_day}.clk"

        filenames.append(sp3_filename)
        filenames.append(clk_filename)
    
    return filenames

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

# --- Main Flask route ---
@upload_rinex.route("/", methods=["GET", "POST"])
def upload_ri():
    success_message = None
    error_message = None
    met_success_message = None 

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
        shutil.copy("model/ppp", os.path.join(subfolder_path, "ppp"))

        # Save RINEX file
        file_path = os.path.join(subfolder_path, file.filename)
        file.save(file_path)

        # --- Read form values and save to .txt ---
        param_values = {
            "ut_days": request.form.get("ut_days"),
            "dynamics": request.form.get("dynamics"),
            "observation": request.form.get("observation"),
            "frequency": request.form.get("frequency"),
            "ephemeris": request.form.get("ephemeris"),
            "product": request.form.get("product"),
            "clock_interp": request.form.get("clock_interp"),
            "iono": request.form.get("iono"),
            "solve_coord": request.form.get("solve_coord"),
            "trop": request.form.get("trop"),
            "backward": request.form.get("backward"),
            "ref_sys": request.form.get("ref_sys"),
            "coord_sys": request.form.get("coord_sys"),
            "pseudo_sigma": request.form.get("pseudo_sigma"),
            "phase_sigma": request.form.get("phase_sigma"),
            "latitude": request.form.get("latitude"),
            "longitude": request.form.get("longitude"),
            "height": request.form.get("height"),
            "antenna_height": request.form.get("antenna_height"),
            "elevation_cutoff": request.form.get("elevation_cutoff"),
            "gdop_cutoff": request.form.get("gdop_cutoff"),
        }

        param_text = f"""\
' UT DAYS OBSERVED                     (1-15):'               {param_values['ut_days']}
' USER DYNAMICS         (1=STATIC,2=KINEMATIC)'               {param_values['dynamics']}
' OBSERVATION TO PROCESS         (1=COD,2=C&P)'               {param_values['observation']}
' FREQUENCY TO PROCESS        (1=L1,2=L2,3=L3)'               {param_values['frequency']}
' SATELLITE EPHEMERIS INPUT     (1=BRD ,2=SP3)'               {param_values['ephemeris']}
' SATELLITE PRODUCT    (1=NO,2=PrcClk,3=MRTCA)'               {param_values['product']}
' SATELLITE CLOCK INTERPOLATION   (1=NO,2=YES)'               {param_values['clock_interp']}
' IONOSPHERIC GRID INPUT          (1=NO,2=YES)'               {param_values['iono']}
' SOLVE STATION COORDINATES       (1=NO,2=YES)'               {param_values['solve_coord']}
' SOLVE TROP. (1=NO,2-5=RW MM/HR) (+100=grad) '               {param_values['trop']}
' BACWARD SUBSTITUTION            (1=NO,2=YES)'               {param_values['backward']}
' REFERENCE SYSTEM            (1=NAD83,2=ITRF)'               {param_values['ref_sys']}
' COORDINATE SYSTEM(1=ELLIPSOIDAL,2=CARTESIAN)'               {param_values['coord_sys']}
' A-PRIORI PSEUDORANGE SIGMA               (m)'           {param_values['pseudo_sigma']}
' A-PRIORI CARRIER PHASE SIGMA             (m)'            {param_values['phase_sigma']}
' LATITUDE  (ddmmss.sss,+N) or ECEF X      (m)'           {param_values['latitude']}
' LONGITUDE (ddmmss.sss,+E) or ECEF Y      (m)'           {param_values['longitude']}
' HEIGHT (m)                or ECEF Z      (m)'           {param_values['height']}
' ANTENNA HEIGHT                           (m)'           {param_values['antenna_height']}
' CUTOFF ELEVATION                       (deg)'          {param_values['elevation_cutoff']}
' GDOP CUTOFF                                 '          {param_values['gdop_cutoff']}
"""

        if request.method == "POST":
            ...
            # Meteorological data
            metro_values = {
                "temperature": float(request.form.get("temperature", 20.0)),
                "pressure": float(request.form.get("pressure", 877.189)),
                "humidity": float(request.form.get("humidity", 50.0)),
                "trop_scale": float(request.form.get("trop_scale", 1.0)),
            }
            met_success_message = "✅ Meteorological data received successfully!"



        param_filename = "L3phase.cmd"
        param_path = os.path.join(subfolder_path, param_filename)
        with open(param_path, 'w') as f:
            f.write(param_text)




        # --- Extract date and download GNSS products ---
        extracted_day = extract_day(file.filename)
        extracted_month = extract_month(file.filename)
        extracted_year = extract_year(file.filename)
        
        if all([extracted_day, extracted_month, extracted_year]):
            full_date = dt.datetime(int("20" + extracted_year), int(extracted_month), int(extracted_day))
            gps_week, gps_day = gps_week_and_day(full_date)

            downloader(gps_week, gps_day, int(param_values["ut_days"]), subfolder_path)
            
            igr_filenames = generate_igr_filenames(gps_week, gps_day, int(param_values["ut_days"]))

            input_tex = f"""\
{file.filename}
{param_filename}
0,0
1 {int(metro_values["temperature"])}
2 {int(metro_values["pressure"])}
3 {int(metro_values["humidity"])}
4 {int(metro_values["trop_scale"])}
0,0
""" + "\n" + "\n".join(igr_filenames)

            input_file_name = "ppp.inp"
            input_path = os.path.join(subfolder_path, input_file_name)
            with open(input_path, 'w') as f:
                f.write(input_tex)



            success_message = (
                f"✅ File uploaded successfully! Observation Date: {extracted_day}/"
                f"{extracted_month}/20{extracted_year}. GPS Week: {gps_week}, Day: {gps_day}."
            )
        else:
            success_message = f"✅ File uploaded to folder '{file_basename}'! (Date not extracted)"

    return render_template("home.html", success_message=success_message, error_message=error_message,met_success_message=met_success_message)
