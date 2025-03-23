from flask import Blueprint , render_template

view = Blueprint("view",__name__)

@view.route("/")  # Route for home page
def home():
    return render_template("home.html" )  # Show home.html

@view.route("/about")  # Route for about page
def about():
    with open("about.txt","r") as file :
        content = file.read()
    return render_template("about.html",content=content)  # Show about.html