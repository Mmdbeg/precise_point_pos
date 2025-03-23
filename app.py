from flask import Flask
import os
from view import view  # Ensure this file exists
from upload_rinex import upload_rinex  # Ensure this file exists

app = Flask(__name__)

# Ensure the upload folder exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Register Blueprints
app.register_blueprint(view)  # This should be correctly defined in view.py
app.register_blueprint(upload_rinex, url_prefix="/upload")  # Should be in upload_rinex.py

if __name__ == "__main__":
    app.run(debug=True)
