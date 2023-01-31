import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

import time
from datetime import datetime

from extras import login_required

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///ultimate_finance.db")

type_of_user = ["Personal", "Enterprise", "Personal & Enterprise"]
expertise = ["Begginer", "Intermediate", "Expert"]  


@app.after_request
def after_request(response):
    #Ensure responses aren't cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/history")
@login_required
def history():
    #Show history of transactions#
    return render_template("history.html")

@app.route("/taxes", methods=["GET", "POST"])
@login_required
def taxes():
    if request.method == "GET":

        # show list of taxes
        user_id = session["user_id"]

        taxes = db.execute("SELECT * FROM taxes_per_user WHERE user_id = ?", user_id)
        
        return render_template("taxes.html", taxes=taxes)

    return render_template("new_tax.html") 

@app.route("/new_tax", methods=["GET", "POST"])
@login_required
def new_tax():
    
    taxes = db.execute("SELECT * FROM taxes")

    if request.method == "POST":
        
        request.form.get("username")

        return render_template("new_tax.html", taxes=taxes)

    return render_template("new_tax.html", taxes=taxes) 


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/")
@login_required
def index():
    
    if request.method == "GET":

        user_id = session["user_id"]

        name = db.execute("SELECT name FROM users WHERE id = ?", user_id)

        return render_template("index.html", name=name)

    return render_template("/")


@app.route("/logout")
def logout():
    #Log user out#

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    
    ##if request.method == "POST":
        
    user_id = session["user_id"]

    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    
    return render_template("settings.html", user=user)

    ##return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        
        if not request.form.get("username"):
            flash(u'Must provide username', 'error')
            return render_template("register.html", type_of_user= type_of_user, expertise=expertise)

        if not request.form.get("password"):
            flash(u'must provide password', 'error')
            return render_template("register.html", type_of_user= type_of_user, expertise=expertise)

        if not request.form.get("confirmation"):
            flash(u'Must provide confirmation password', 'error')
            return render_template("register.html", type_of_user= type_of_user, expertise=expertise)

        if request.form.get("password") != request.form.get("confirmation"):
            flash(u'Passwords must match', 'error')
            return render_template("register.html", type_of_user= type_of_user, expertise=expertise)

        if not request.form.get("type_of_user"):
            flash(u'Must provide a type of user', 'error')
            return render_template("register.html", type_of_user= type_of_user, expertise=expertise)

        if not request.form.get("expertise"):
            flash(u'Must provide an expertise', 'error')
            return render_template("register.html", type_of_user= type_of_user, expertise=expertise)

        # checking for username in db
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username not taken
        if len(rows) != 0:
            flash(u'Username has already been taken', 'error')
            return render_template("register.html", type_of_user= type_of_user, expertise=expertise)

        db_username = request.form.get("username")
        db_hashed_password = generate_password_hash(request.form.get("password"))
        db_type_of_user = request.form.get("type_of_user")
        db_expertise = request.form.get("expertise")

        prim_key = db.execute("INSERT INTO users (username, hash, type_of_user, expertise) VALUES (:username, :hash, :type_of_user, :expertise)", username=db_username,hash=db_hashed_password, type_of_user=db_type_of_user, expertise=db_expertise)

        if prim_key is None:
            flash(u'Registration error', 'error')

        # remember user session
        session["user_id"] = prim_key

        flash("Welcome to Ultimate Finance! Here you will be able to manage your personal finances.")

        return redirect("/")

    else:
        return render_template("register.html", type_of_user= type_of_user, expertise=expertise)
