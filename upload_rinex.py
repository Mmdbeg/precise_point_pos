import os
from flask import Blueprint, request, render_template
import datetime as dt
import subprocess
import shutil
from functions import *

upload_rinex = Blueprint("upload_rinex", __name__)

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

        upload_folder = "uploads"
        file_basename = os.path.splitext(file.filename)[0]
        subfolder_path = os.path.join(upload_folder, file_basename)
        os.makedirs(subfolder_path, exist_ok=True)
        shutil.copy("model/ppp", os.path.join(subfolder_path, "ppp"))
        shutil.copy("model/runner.sh", os.path.join(subfolder_path, "runner.sh"))


        file_path = os.path.join(subfolder_path, file.filename)
        file.save(file_path)

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

        metro_values = {
            "temperature": float(request.form.get("temperature")),
            "pressure": float(request.form.get("pressure")),
            "humidity": float(request.form.get("humidity")),
            "trop_scale": float(request.form.get("trop_scale")),
        }
        met_success_message = "✅ Meteorological data received successfully!"

        param_filename = "L3phase.stat.cmd"
        param_path = os.path.join(subfolder_path, param_filename)
        with open(param_path, 'w', newline='\n') as f:
            f.write(param_text)

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
1 {float(metro_values["temperature"])}
2 {float(metro_values["pressure"])}
3 {float(metro_values["humidity"])}
4 {float(metro_values["trop_scale"])}
0,0""" + "\n" + "\n".join(igr_filenames)

            input_file_name = "ppp.stat.inp"
            input_path = os.path.join(subfolder_path, input_file_name)
            with open(input_path, 'w', newline='\n') as f:
                f.write(input_tex)
 
            subprocess.run("./runner.sh", shell=True, cwd=f'{subfolder_path}')

            sum_file_path = os.path.join(subfolder_path, f"{file_basename}.sum")
            estimate_text, diff_text = parse_sum_file(sum_file_path)







            success_message = (
                f"✅ File uploaded and processed! Observation Date: {extracted_day}/"
                f"{extracted_month}/20{extracted_year}. GPS Week: {gps_week}, Day: {gps_day}."
            )
        else:
            success_message = f"✅ File uploaded to folder '{file_basename}'! (Date not extracted)"

    return render_template(
    "home.html",
    success_message=success_message,
    error_message=error_message,
    met_success_message=met_success_message,
    estimate_text=estimate_text,
    diff_text=diff_text,
)

