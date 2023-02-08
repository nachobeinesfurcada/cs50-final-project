# KISS
# HOT RELOADING export FLASK_ENV=development
# HOT RELOADING export FLASK_APP=app
import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

import pandas as pd
import time
from datetime import date, datetime, timedelta
from extras import login_required

# for API


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

currencies = ["ARS","REAL", "USD"]

days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

""" IN DEVELOPMENT
# API for Dolar Blue
URL = 'https://www.dolarsi.com/api/api.php?type=valoresprincipales'
json = requests.get(URL).json()

BLUE_COMPRA = 0
BLUE_VENTA = 0 

for index, name in range(1):
    BLUE_COMPRA = json[index]['casa']['compra']
    BLUE_VENTA = json[index]['casa']['venta']
"""


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
            flash(u'Must provide username', 'error')

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash(u'Must provide password', 'error')

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash(u'invalid username or password', 'error')

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
    user_id = session["user_id"] 
    name = db.execute("SELECT name FROM users WHERE id = ?", user_id)

    if request.method == "GET":

        return render_template("index.html", name=name)

    return render_template("/", name=name)


@app.route("/logout")
def logout():
    #Log user out#

    # Forget any user_id
    session.clear()
    session["name"] = None

    # Redirect user to login form
    return redirect("/")



@app.route("/new_plan", methods=["GET", "POST"])
@login_required
def new_plan():
        
    # get user id to pass as a list to html 
    user_id = session["user_id"]
    name = db.execute("SELECT name FROM users WHERE id = ?", user_id)
    
    # get list of expenses
    expenses = db.execute("SELECT * FROM expenses WHERE user_id = ?", user_id)
    
    #get time on real time
    now = datetime.now()

    # get list of incomes
    incomes = db.execute("SELECT * FROM incomes WHERE user_id = ?", user_id)
    
    if request.method == "POST":
    
        # PERIOD DEFINITION
        if request.form.get("day"):
            # calculate today and send it to template
            period = now.strftime("%A %d, %b of %Y")
            return render_template("new_plan.html", period=period, name=name, currencies=currencies)

        if request.form.get("month"):
            # calculate 1 month from today and send it to template
            this_month = now.strftime("%Y-%m-%d")
            next_month = (pd.to_datetime(this_month)+pd.DateOffset(months=1)).strftime("%Y-%m-%d")
            period = f"1 Month. \nFrom: {this_month} to {next_month}"
            return render_template("new_plan.html", period=period, name=name,currencies=currencies)

        if request.form.get("quarter"):
            # calculate 3 months from today and send it to template
            this_month = now.strftime("%Y-%m-%d")
            next_month = (pd.to_datetime(this_month)+pd.DateOffset(months=3)).strftime("%Y-%m-%d")
            period = f"1 quarter. \nFrom: {this_month} to {next_month}"
            return render_template("new_plan.html", period=period, name=name,currencies=currencies)

        if request.form.get("year"):
            # calculate 12 month from today and send it to template
            this_month = now.strftime("%Y-%m-%d")
            next_month = (pd.to_datetime(this_month)+pd.DateOffset(months=12)).strftime("%Y-%m-%d")
            period = f"1 year. \nFrom: {this_month} to {next_month}"
            return render_template("new_plan.html", period=period, name=name,currencies=currencies)
        
        # INCOME
        
        # get input from form
        income_name = request.form.get("income_name")
        currency = request.form.get("currency")
        income = request.form.get("income")
                 
        

        # validate if all fields are filled out
        if income_name is None:
            flash("Please select a income name.")
            return redirect("/new_plan")

        if currency is None:
            flash("Please insert an currency.")
            return redirect("/new_plan")

        if income is None:
            flash("Please insert an income amount.")
            return redirect("/new_plan")            

        # prim_key to check for succesfull data entry 
        prim_key = db.execute("INSERT INTO incomes (day_added, name, user_id, income, currency) VALUES (:day_added, :name, :user_id, :income, :currency)",
                                day_added=now,
                                name=income_name,
                                user_id=user_id,
                                income=income,
                                currency=currency)
        if prim_key is None:
                flash("Error. Please contact support")
                return redirect("/new_plan")
        else:
            flash("Income added!")
        
            
        return render_template("new_plan.html", name=name)
        
    return render_template("new_plan.html", name=name, currencies=currencies, expenses=expenses, incomes=incomes) 

@app.route("/add_expense", methods=["GET", "POST"])
@login_required
def add_expense():
    
    user_id = session["user_id"]
    name = db.execute("SELECT name FROM users WHERE id = ?", user_id)
    
    expenses = db.execute("SELECT * FROM expenses WHERE user_id = ?", user_id)

    if request.method == "POST":

        expense_name = request.form.get("ExpenseName")
        expense_desc = request.form.get("ExpenseDescription")

        if not expense_name:
            flash(u'Must provide an Expense Name', 'error')
            return redirect("add_expense")

        timestamp = time.time()
        date_time = datetime.fromtimestamp(timestamp)
        
        # if description is not null:
        if expense_desc is not None:
            prim_key = db.execute("INSERT INTO expenses (day_added, name, description, user_id) VALUES (:day_added, :name, :description, :user_id)",
                                  day_added=date_time,
                                  name=expense_name,
                                  description=expense_desc,
                                  user_id=user_id)

            if prim_key is None:
                flash("Error. Please contact support")
                return redirect("/new_plan")
                
            flash(u'Expense  Added!')

        elif not expense_desc:
            prim_key = db.execute("INSERT INTO expenses (day_added, name, user_id) VALUES (:day_added, :name, :user_id)",
                                  day_added=date_time,
                                  name=expense_name,
                                  user_id=user_id)

            if prim_key is None:
                flash("Error. Please contact support")
                return redirect("/add_expense")   

            flash(u'Expense  Added!')    

        return redirect("/add_expense")

    return render_template("add_expense.html", expenses=expenses)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    
    ## if request.method == "POST":
        
    user_id = session["user_id"]

    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    
    return render_template("settings.html", user=user)

    ##return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        
        db_username = request.form.get("username")
        db_hashed_password = generate_password_hash(request.form.get("password"))
        db_type_of_user = request.form.get("type_of_user")
        db_expertise = request.form.get("expertise")
        db_name = request.form.get("name")
        db_lastname = request.form.get("lastname")
        db_birth = request.form.get("birth")

        if not db_username:
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

        if not db_name:
            flash(u'Must provide a valid name', 'error')
            return render_template("register.html", type_of_user= type_of_user, expertise=expertise)

        if not db_lastname:
            flash(u'Must provide a last name', 'error')
            return render_template("register.html", type_of_user= type_of_user, expertise=expertise)

        if not db_type_of_user:
            flash(u'Must provide a type of user', 'error')
            return render_template("register.html", type_of_user= type_of_user, expertise=expertise)

        if not db_expertise:
            flash(u'Must provide an expertise', 'error')
            return render_template("register.html", type_of_user= type_of_user, expertise=expertise)

        if not db_birth:
            flash(u'Must provide a birth date', 'error')
            return render_template("register.html", type_of_user= type_of_user, expertise=expertise)

        # checking for username in db
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username not taken
        if len(rows) != 0:
            flash(u'Username has already been taken', 'error')
            return render_template("register.html", type_of_user= type_of_user, expertise=expertise)


        prim_key = db.execute("INSERT INTO users (username, hash, type_of_user, expertise, name, lastname, birth) VALUES (:username, :hash, :type_of_user, :expertise, :name, :lastname, :birth)", username=db_username,hash=db_hashed_password, type_of_user=db_type_of_user, expertise=db_expertise, name=db_name, lastname=db_lastname, birth=db_birth)

        if prim_key is None:
            flash(u'Registration error', 'error')
            
        # remember user session
        session["user_id"] = prim_key

        flash("Welcome to Ultimate Finance! Here you will be able to manage your personal finances.")

        return redirect("/")

    else:
        return render_template("register.html", type_of_user= type_of_user, expertise=expertise)
