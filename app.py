# import openai
from flask import Flask, request, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
import requests

url = "https://openai80.p.rapidapi.com/chat/completions"

headers = {
    "Content-Type": "application/json",
    "X-RapidAPI-Key": "d84fca7d4emshd10e32a65c27c6ep19764ejsn800030a17dc2",
    "X-RapidAPI-Host": "openai80.p.rapidapi.com",
}


app = Flask(__name__)

# app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:@localhost/loginpage'
# db=SQLAlchemy(app)

# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)

app.secret_key = "vishnuvardhanreddy"


class user_details(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)


with app.app_context():
    db.create_all()

# # Set up OpenAI API credentials
# openai.api_key = "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"

# # Set up OpenAI completion engine
# engine_id = "text-davinci-003"

history = []


@app.route("/")
def loading():
    return render_template("loading.html")


@app.route("/landingpage")
def landing_page():
    return render_template("getting_started.html")


# Define a decorator to check if the user is authenticated
def login_required(f):
    def wrapper(*args, **kwargs):
        if "user_id" in session:
            # If the user is authenticated, call the function
            return f(*args, **kwargs)
        else:
            # If the user is not authenticated, redirect to the login page
            return redirect("/login")

    return wrapper


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    history.clear()

    if request.method == "POST":
        email = request.form["username"]
        password = request.form["password"]

        user = user_details.query.filter_by(email=email, password=password).first()
        if user:
            # Set the user ID in the session
            session["user_id"] = user.email
            # If the login is successful, redirect to the home page
            return redirect("/home")
        else:
            return render_template("login.html", error="Invalid email or password")
    else:
        return render_template("login.html")


# User registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get the email and password from the form
        email = request.form["username"]
        password = request.form["password"]

        # Check if the email already exists in the database
        user = user_details.query.filter_by(email=email).first()
        if user:
            # If the email already exists, render the register page with an error message
            return render_template(
                "register.html", error="User already exists please login"
            )
        else:
            # If the email does not exist, add the user to the database and redirect to the login page
            new_user = user_details(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")
    else:
        # If the request method is GET, render the register page
        return render_template("register.html")


@app.route("/home")
@login_required
def index():
    # Render the template with the chat history
    return render_template("index.html", history=history)


@app.route("/message", methods=["POST"])
def message():
    # Get the user's message from the request
    user_message = request.form["message"]

    # # Send the user's message to the OpenAI completion engine
    # response = openai.Completion.create(
    #     engine=engine_id,
    #     prompt=f"User: {user_message}\nAI:",
    #     max_tokens=250,
    #     n=1,
    #     stop=None,
    #     temperature=0.7
    # )

    # Extract the AI's response from the OpenAI response
    # ai_message = response.choices[0].text.strip()
    ##########################################################################################################################

    # def chat(prompt):
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": user_message}],
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        ai_message = response.json()["choices"][0]["message"]["content"]
    else:
        ai_message = "Error: " + response.text

    # # start the chat
    # print("Chat with the OpenAI GPT-3 chatbot!")
    # while True:
    #     user_input = input("You: ")
    #     chatbot_output = chat(user_input)
    #     print("Bot: " + chatbot_output)
    #########################################################################################################################

    # Add the messages to the chat history
    history.append(("User", user_message))
    history.append(("AI", ai_message))

    # Render the template with the updated chat history
    return render_template("index.html", history=history)


# @app.route("/login",methods=['GET','POST'])
# def home():
#   if request.method=='POST':
#     email=request.form.get('username')
#     password=request.form.get('password')

#     entry=user_details(email=email,password=password)
#     db.session.add(entry)
#     db.session.commit()
#   return render_template("login.html")


# @app.route("/picto", methods=["GET", "POST"])
# def picto():
#     if request.method == "POST":
#         prompt = request.form["prompt"]
#         response = openai.Image.create(prompt=prompt, n=2, size="256x256")
#         url = response.data[0].url
#         return render_template("result.html", url=url, prompt=prompt)
#     return render_template("picto.html")


@app.route("/about")
def about_electrika():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
