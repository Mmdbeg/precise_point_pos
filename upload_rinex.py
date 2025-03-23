import os
import subprocess
from flask import Blueprint, request, render_template

upload_rinex = Blueprint("upload_rinex", __name__)

@upload_rinex.route("/", methods=["GET", "POST"])  # Keep it "/"
def upload_ri():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part"
        
        file = request.files["file"]
        if file.filename == "":
            return "No selected file"
        
        upload_folder = "uploads"
        os.makedirs(upload_folder, exist_ok=True)  # Ensure folder exists
        
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
         
        # passing file path to bash script 
        subprocess.run(["bash","main_app.sh",file_path]) 

        
        #print(f"✅ File saved at: {file_path}")  # Print file path for debugging
        
        return f"File uploaded to path [ {file_path} ] successfully! were working on your observation file"
    
    return render_template("upload.html")  # Use an HTML template instead of raw text

