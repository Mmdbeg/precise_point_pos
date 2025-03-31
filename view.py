from flask import Blueprint, render_template
import os

view = Blueprint("view", __name__)

# Get the project's root directory (assuming 'view.py' is inside 'precise_point_pos')
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  

# Construct the absolute path to "about.txt"
ABOUT_FILE_PATH = os.path.join(BASE_DIR, "precise_point_pos", "about.txt")


@view.route("/")  # Route for home page
def home():
    return render_template("home.html")  # Show home.html


@view.route("/about")  # Route for about page
def about():
    try:
        with open(ABOUT_FILE_PATH, "r") as file:
            content = file.read()
    except FileNotFoundError:
        content = "⚠️ about.txt not found!"

    return render_template("about.html", content=content)  # Show about.html
