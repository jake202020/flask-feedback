"""Flask Feedback app for practicing logged in user functionality"""

from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import RegisterForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///flask_feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.route("/")
def register():
    """Redirect to register page"""

    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def registration_form():
    """Show a registration form (GET) or create a new user and show secret page (POST)"""

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data
        email = form.email.data 
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username, pwd, email, first_name, last_name)
        db.session.add(user)
        db.session.commit()

        # session["user_id"] = user.id
        flash("User successfully created")
        # on successful login, redirect to secret page
        return redirect("/secret")

    else:
        return render_template("register.html", form=form)