import os
from flask import Blueprint, request, render_template
import re
import subprocess

upload_rinex = Blueprint("upload_rinex", __name__)

def extract_number(filename):
    match = re.search(r'GEOP(\d{3})', filename)
    return match.group(1) if match else None

def year_extract(filename):
    match = re.search(r"\.(\d{2})o", filename)  # Fixed regex
    return match.group(1) if match else None

@upload_rinex.route("/", methods=["GET", "POST"])
def upload_ri():
    success_message = None
    error_message = None

    if request.method == "POST":
        if "file" not in request.files:
            error_message = "⚠️ No file part in the request!"
            return render_template("home.html", success_message=success_message, error_message=error_message)

        file = request.files["file"]
        if file.filename == "":
            error_message = "⚠️ No file selected!"
            return render_template("home.html", success_message=success_message, error_message=error_message)

        upload_folder = "uploads"
        os.makedirs(upload_folder, exist_ok=True)  # Ensure folder exists

        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)

        # Extract number from filename
        extracted_number = extract_number(file.filename)
        extracted_year = year_extract(file.filename)  # Fixed variable name

        if extracted_number and extracted_year:  
            success_message = f"✅ File uploaded successfully! Your file was recorded on day {extracted_number} of year 20{extracted_year}."

         
        else:
            success_message = "✅ File uploaded successfully! Could not extract full date information from filename."

    return render_template("home.html", success_message=success_message, error_message=error_message)
