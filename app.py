##############3/////////////////////GEMINI PRO///////////////////////#######################################

import google.generativeai as genai
from colorama import Fore
from flask import Flask, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()
# Google Gen AI configuration
genai.configure(api_key=os.getenv("API_KEY"))

app = Flask(__name__)

# Database configuration
db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)
app.secret_key = "vishnuvardhanreddy"


# User details model
class user_details(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)


with app.app_context():
    db.create_all()

history = []


@app.route("/")
def loading():
    return render_template("loading.html")


@app.route("/landingpage")
def landing_page():
    return render_template("getting_started.html")


def login_required(f):
    def wrapper(*args, **kwargs):
        if "user_id" in session:
            return f(*args, **kwargs)
        else:
            return redirect("/login")

    return wrapper


# @app.route("/login", methods=["GET", "POST"])
# def login():
#     history.clear()

#     if request.method == "POST":
#         email = request.form["username"]
#         password = request.form["password"]


#         user = user_details.query.filter_by(email=email, password=password).first()
#         if user:
#             session["user_id"] = user.email
#             return redirect("/home")
#         else:
#             return render_template("login.html", error="Invalid email or password")
#     else:
#         return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    history.clear()

    if request.method == "POST":
        email = request.form["username"]
        password = request.form["password"]

        user = user_details.query.filter_by(email=email, password=password).first()
        if user:
            session["user_id"] = user.sno  # Use a unique identifier, such as user ID
            return redirect("/home")
        else:
            return render_template("login.html", error="Invalid email or password")
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["username"]
        password = request.form["password"]

        user = user_details.query.filter_by(email=email).first()
        if user:
            return render_template(
                "register.html", error="User already exists, please login"
            )
        else:
            new_user = user_details(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/home")
@login_required
def index():
    user_id = session.get("user_id")
    user = user_details.query.filter_by(sno=user_id).first()

    return render_template("index.html", history=history, user=user)


@app.route("/message", methods=["POST"])
def message():
    user_message = request.form["message"]

    response = genai.GenerativeModel("gemini-pro").generate_content(user_message)
    ai_message = response.text

    history.append(("User", user_message))
    history.append(("AI", ai_message))

    return render_template("index.html", history=history)


@app.route("/about")
def about_electrika():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
