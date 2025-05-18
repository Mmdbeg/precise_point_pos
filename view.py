from flask import Blueprint, render_template
import os

view = Blueprint("view", __name__)


@view.route("/")  # Route for home page
def home():
    return render_template("home.html")  # Show home.html


@view.route("/about")  # Route for about page
def about():

    return render_template("about.html")  # Show about.html
