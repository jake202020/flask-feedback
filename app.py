"""Flask Feedback app for practicing logged in user functionality"""

from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///flask_feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

# Create database tables from models.py
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.route("/")
def register():
    """Redirect to register page"""
    users = User.query.all()

    return render_template("users.html", users=users)

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

        # Add username to session for authorization
        session["username"] = user.username

        flash("User successfully created")
        # on successful login, redirect to secret page
        return redirect(f"/users/{ username }")

    else:
        return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login_form():
    """Show a login form (GET) or login a new user and show secret page (POST)"""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(username, pwd)

        if user:
            flash("Login successful")

            # Add username to session for authorization
            session["username"] = user.username

            # on successful login, redirect to secret page
            return redirect(f"/users/{ username }")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)

@app.route("/users/<username>")
def user_page(username):
    """Show logged in  user information"""

    if "username" in session:
        user = User.query.get_or_404(username)
        feedback = Feedback.query.filter_by(username=username)

        return render_template("user_info.html", user=user, feedback=feedback)

    flash("Need to be logged in first")
    return redirect("/login")

@app.route("/users/<username>/delete")
def delete_user(username):
    """Delete current user"""

    if "username" in session:
        user = User.query.get_or_404(username)
        
        if user.username == session['username']:
            user = User.query.get(username)
            db.session.delete(user)
            db.session.commit()

            session.pop("username")
            return redirect("/register")

        flash("You do not have permission to do that")
        return redirect("/")

    flash("Need to be logged in first")
    return redirect("/login")

@app.route("/users/<username>/feedback/add", methods=['GET', 'POST'])
def feedback(username):
    """Show feedback form (GET) or add feedback to db (POST)"""

    if "username" in session:
        form = FeedbackForm()
        user = User.query.get_or_404(username)

        if user.username == session['username']:
            if form.validate_on_submit():
                title = form.title.data
                content = form.content.data
                username = user.username

                # create a feedback instance
                feedback = Feedback(title=title, content=content, username=username)
                db.session.add(feedback)
                db.session.commit()

                return redirect(f"/users/{ username }")

            return render_template("feedback_form.html", form=form)
        else:
            flash("You do not have permission to edit that")
            return redirect(f"/users/{ session['username'] }")
    else:
        flash("Need to be logged in to submit feedback")
        return render_template("login.html", form=form)

@app.route("/feedback/<int:feedback_id>/update", methods=['GET', 'POST'])
def edit_feedback(feedback_id):
    """Allow user who created a feedback to edit it"""

    if "username" in session:
        feedback = Feedback.query.get_or_404(feedback_id)
        user = User.query.get_or_404(feedback.user.username)

        if user.username == session['username']:
            form = FeedbackForm(title=feedback.title, content=feedback.content)
            
            if form.validate_on_submit():
                feedback.title = form.title.data
                feedback.content = form.content.data

                db.session.add(feedback)
                db.session.commit()

                return redirect(f"/users/{ user.username }")

            return render_template("feedback_form.html", form=form)
        else:
            flash("You do not have permission to edit that")
            return redirect("/")
    else:
        flash("Need to be logged in to edit feedback")
        return render_template("login.html", form=form)

@app.route("/feedback/<int:feedback_id>/delete")
def delete_feedback(feedback_id):
    """Allow user who created a feedback to delete it"""
    if "username" in session:
        feedback = Feedback.query.get_or_404(feedback_id)
        user = User.query.get_or_404(feedback.user.username)

        if user.username == session['username']:            

            db.session.delete(feedback)
            db.session.commit()

            return redirect(f"/users/{ user.username }")

        else:
            flash("You do not have permission to delete that")
            return redirect("/")
    else:
        flash("Need to be logged in to delete feedback")
        return render_template("login.html", form=form)

@app.route("/logout")
def logout_user():
    """Logout current logged in user"""

    session.pop("username")
    return redirect("/login")