from flask import Flask
import os
import subprocess
from view import view  # Ensure this file exists
from upload_rinex import upload_rinex

app = Flask(__name__)

# Ensure the upload folder exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Register Blueprints
app.register_blueprint(view)  
app.register_blueprint(upload_rinex, url_prefix="/upload") 


if __name__ == "__main__":
    app.run(debug=True)
