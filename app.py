# HOT RELOADING export FLASK_ENV=development
# HOT RELOADING export FLASK_APP=app
import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.datastructures import ImmutableMultiDict

import pandas as pd
import time
from datetime import datetime, date
from extras import login_required, MagerDicts

import babel.numbers


# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///personances.db")

type_of_user = ["Personal", "Enterprise", "Personal & Enterprise"]
expertise = ["Begginer", "Intermediate", "Expert"]  

currencies = ["ARS","REAL", "USD"]

days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

periods = ["Day", "Month", "Quarter", "Year"]

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

@app.route('/user_id/', defaults={'subject' : '/'})
@app.route('/user_id/<user_id>')
def subject(subject):
    
    return 'The value is: ' + subject

@app.after_request
def after_request(response):
    #Ensure responses aren't cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response




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

    # user data
    user_id = session["user_id"] 
    name = db.execute("SELECT name FROM users WHERE id = ?", user_id)

    # todays date
    today = date.today()

    # Get latest plan_id
    try:
        plan_id_index = db.execute("SELECT id, name FROM plans WHERE user_id = ? ORDER BY id DESC limit 1", user_id)
        if len(plan_id_index) == 0:
            return redirect("new_plan")

        index = plan_id_index[0]
        plan_id = index["id"]
        plan_name = index["name"]
    
    except:
        return redirect("new_plan")
    
    # get latest currency
    currency_index = db.execute("SELECT currency FROM incomes WHERE user_id = ? AND plan_id = ? ORDER BY plan_id DESC limit 1", user_id, plan_id)
    index = currency_index[0]
    latest_currency= index["currency"]


    incomes = db.execute("SELECT name, sum(income) AS income FROM incomes WHERE user_id = ? AND plan_id = ? GROUP BY name ORDER BY day_added ASC", user_id, plan_id)
    expenses = db.execute("SELECT name, sum(expense) as expense FROM expenses WHERE user_id = ? AND plan_id=? GROUP BY name", user_id, plan_id)
    plan = db.execute("SELECT * FROM plans WHERE user_id = ? AND id = ?;", user_id, plan_id)
        
    # formating the data into a list for it to be user on the javascript file    
    currplan_income_data = []
    for row in incomes:
        currplan_income_data.append([row['name'], row['income']])

    # formating the data into a list for it to be user on the javascript file        
    currplan_expense_data = []
    for row in expenses:
        currplan_expense_data.append([row['name'], row['expense']])

    # ALL INCOMES and EXPENSES from all plans

    all_incomes = db.execute("SELECT name, sum(income) AS income FROM incomes WHERE user_id = ? GROUP BY name", user_id)
    all_expenses = db.execute("SELECT name, sum(expense) AS expense FROM expenses WHERE user_id = ? GROUP BY name", user_id)

    # formating the data into a list for it to be user on the javascript file    
    all_income_data = []
    for row in all_incomes:
        all_income_data.append([row['name'], row['income']])

    # formating the data into a list for it to be user on the javascript file        
    all_expense_data = []
    for row in all_expenses:
        all_expense_data.append([row['name'], row['expense']])


    # creating variables for analysis
    result_over_weeks = 0
    num_plans = 0

    #check if there is already a plan created
    if plan is not None: 

        plan_index = plan[0]
        # creating an index variable for easy treatment
        if not incomes:
            incomes = 0
        else:
            income_index = incomes[0]

        if not expenses:
            expenses = 0
        else:     
            expense_index = expenses[0]

        #calculate result / 4 (for weekend expenses)
        result_over_weeks = int(plan_index["result"]) / 4

       
       
        # USER DATA
        
        # number of plans
        numplans = db.execute("SELECT count(id) as num_plans FROM plans WHERE user_id=?", user_id)
        index = numplans[0]
        num_plans = index["num_plans"]

        # total income from beggining of year
        this_year = today.year
        ti = db.execute("SELECT sum(income) AS total_income FROM incomes WHERE user_id=? AND strftime('%Y',day_added) LIKE (select strftime('%Y','now'))", user_id)
        index = ti[0]
        total_income_from_this_year = index["total_income"]
        total_income_from_this_year_formatted = babel.numbers.format_currency(total_income_from_this_year, '$', locale="en_US")

        # total income from beggining of year
        te = db.execute("SELECT sum(expense) AS total_expense FROM expenses WHERE user_id=? AND strftime('%Y',day_added) LIKE (select strftime('%Y','now'))", user_id)
        index = te[0]
        total_expense_from_this_year = index["total_expense"]
        total_expense_from_this_year_formatted = babel.numbers.format_currency(total_expense_from_this_year, '$', locale="en_US")

        # percentage of result over income total for this year PER PLAN
        tir = db.execute("SELECT sum(total_income) as total_income FROM plans WHERE user_id=? AND strftime('%Y',day_added) LIKE (select strftime('%Y','now'))", user_id)
        index = tir[0]
        total_income_results = index["total_income"]

        tr = db.execute("SELECT sum(result) as result FROM plans WHERE user_id=? AND strftime('%Y',day_added) LIKE (select strftime('%Y','now'))", user_id)
        index = tr[0]
        total_results = index["result"]    

        percecentage_tr_over_ti = (int(total_results) * 100 / int(total_income_results)) / num_plans
        formated_perc = "{:.0%}". format(percecentage_tr_over_ti)

        # total types of expenses
        total_toe = db.execute("SELECT count(id) as toe FROM types_of_expenses WHERE user_id = ? AND strftime('%Y',day_added) LIKE (select strftime('%Y','now'))", user_id)
        index = total_toe[0]
        total_types_of_expenses = index["toe"]

        # average of income per plan
        average_total_income_per_plan = int(total_income_results) / int(num_plans)
        average_total_income_per_plan_f = babel.numbers.format_currency(average_total_income_per_plan, '$', locale="en_US")

        # average expense per plan
        te = db.execute("SELECT sum(expense) as total_expense FROM expenses WHERE user_id=? AND strftime('%Y',day_added) LIKE (select strftime('%Y','now'))", user_id)
        index = te[0]
        total_expenses = index["total_expense"]
        average_total_expense_per_plan = int(total_expenses) / int(num_plans)
        average_total_expense_per_plan_f = babel.numbers.format_currency(average_total_expense_per_plan, '$', locale="en_US")




    return render_template("index.html", name=name, incomes=incomes, result_over_weeks=result_over_weeks,
                             num_plans=num_plans, this_year=this_year, plan_id=plan_id,
                             total_income_from_this_year_formatted=total_income_from_this_year_formatted,
                             total_expense_from_this_year_formatted=total_expense_from_this_year_formatted,
                             formated_perc=formated_perc, total_types_of_expenses=total_types_of_expenses,
                             average_total_income_per_plan_f=average_total_income_per_plan_f,
                             average_total_expense_per_plan_f=average_total_expense_per_plan_f,
                             latest_currency=latest_currency, currplan_income_data=currplan_income_data, 
                             currplan_expense_data=currplan_expense_data,
                             all_expense_data=all_expense_data, all_income_data=all_income_data,
                             plan_name=plan_name)

@app.route("/logout")
def logout():
    #Log user out#

    # Forget any user_id
    session.clear()
    session["name"] = None

    # Redirect user to login form
    return redirect("/")



@app.route("/plans", methods=["GET", "POST"])
@login_required
def plans():

    user_id = session["user_id"]
    name = db.execute("SELECT name FROM users WHERE id = ?", user_id)
    plans = db.execute("SELECT * FROM plans WHERE user_id = ? ORDER BY id DESC;", user_id)
    
    latest_currency = ""

    plan_id_index = db.execute("SELECT id FROM plans WHERE user_id = ? ORDER BY id DESC limit 1", user_id)
    if len(plan_id_index) != 0:

        index = plan_id_index[0]
        plan_id = index["id"]

        # get latest currency
        currency_index = db.execute("SELECT currency FROM incomes WHERE user_id = ? AND plan_id = ? ORDER BY plan_id DESC limit 1", user_id, plan_id)
        index = currency_index[0]
        latest_currency= index["currency"] 
    else:
        flash("You dont have any plans. To create a new plan, head to New Plan on the heading.")  

    return render_template("plans.html", plans=plans, name=name, latest_currency=latest_currency)



@app.route("/delete_plan/<plan_id>", methods=["GET", "POST"])
@login_required
def delete_plan(plan_id):
    
    user_id = session["user_id"]
    plans = db.execute("SELECT * FROM plans WHERE user_id = ? AND id = ?", user_id, plan_id)

    delete_from_plans = db.execute("DELETE FROM plans WHERE user_id = ? AND id = ?", user_id, plan_id)
    delete_from_incomes = db.execute("DELETE FROM incomes WHERE user_id = ? AND plan_id = ?", user_id, plan_id)
    delete_from_expenses = db.execute("DELETE FROM expenses WHERE user_id = ? AND plan_id = ?", user_id, plan_id)

   
    flash("Plan terminated")  

    return redirect("/plans")


@app.route("/copy_plan/<plan_id>", methods=["GET", "POST"])
@login_required
def copy_plan(plan_id):

    user_id = session["user_id"]
    plans = db.execute("SELECT * FROM plans WHERE user_id = ? AND id = ?;", user_id, plan_id)

    #get time on real time
    day_added = date.today()

    # Indexing all values to single variables for easier treatement with forms and database
    index = plans[0]
    old_plan_id = plan_id
    old_plan_name = index["name"]
    old_PERIOD = index["period"]
    old_total_income = index["total_income"]
    old_total_expense = index["total_expense"]
    old_result = index["result"]

    # create new plan ID by executing a query over plans and past ids
    
    past_id = db.execute("SELECT id FROM plans WHERE user_id=? ORDER BY id DESC limit 1", user_id)
    
    index = past_id[0]
    new_plan_id = index["id"] + 1


    # get list of incomes of OLD plan
    old_incomes = db.execute("SELECT * FROM incomes WHERE user_id = ? AND plan_id=? ORDER BY id ASC", user_id, old_plan_id)
    
    # get list of expenses of OLD plan inner join types of expenses
    old_expenses = db.execute("SELECT * FROM expenses WHERE user_id = ? AND plan_id=? ORDER BY name ASC", user_id, old_plan_id)

    # get list of types of expenses for entering new 
    types_of_expenses = db.execute("SELECT name FROM types_of_expenses WHERE user_id=?;", user_id)


    # DATABASE INSERTS
    new_plan_name = old_plan_name + "[1]"
    # INSERT NEW PLAN INTO PLANS
    prim_key = db.execute("INSERT INTO plans (id, day_added, name, period, total_income, total_expense, result, user_id) VALUES (:new_plan_id, :day_added, :old_plan_name, :old_PERIOD, :old_total_income, :old_total_expense, :old_result, :user_id)",
                new_plan_id=new_plan_id,
                day_added=day_added,
                old_plan_name=new_plan_name,
                old_PERIOD=old_PERIOD,
                old_total_income=old_total_income,
                old_total_expense=old_total_expense,
                old_result=old_result,
                user_id=user_id)

    # iterate over past incomes to INSERT INTO new incomes
    for i in old_incomes:
        curr_name = i["name"]
        curr_currency = i["currency"]
        curr_income = i["income"]

        db.execute("INSERT INTO incomes (day_added, user_id, currency, income, plan_id, name) VALUES (:day_added, :user_id, :curr_currency, :curr_income, :new_plan_id, :curr_name)",
                    day_added=day_added, 
                    user_id=user_id, 
                    curr_currency=curr_currency, 
                    curr_income=curr_income, 
                    new_plan_id=new_plan_id, 
                    curr_name=curr_name)
        
    # iterate over past expenses to INSERT INTO new expenses
    for i in old_expenses:
        curr_name = i["name"]
        curr_expense = i["expense"]

        #insert into database new plan
        db.execute("INSERT INTO expenses (day_added, user_id, plan_id, expense, name) VALUES (:day_added, :user_id, :curr_expense, :new_plan_id, :curr_name)",
                    day_added=day_added, 
                    user_id=user_id, 
                    new_plan_id=new_plan_id,
                    curr_expense=curr_expense, 
                    curr_name=curr_name)

    flash(f"Old plan {old_plan_id} copied. New plan {new_plan_id} added!")

        
    return redirect("/plans")
    


@app.route("/edit_plan/<plan_id>", methods=["GET", "POST"])
@login_required
def edit_plan(plan_id):

    user_id = session["user_id"]
    plans = db.execute("SELECT * FROM plans WHERE user_id = ? AND id = ?;", user_id, plan_id)

    #get time on real time
    now = date.today()

    # Indexing all values to single variables for easier treatement with forms and database
    index = plans[0]
    plan_name = index["name"]
    PERIOD = index["period"]
    total_income = index["total_income"]
    total_income_format = babel.numbers.format_currency(total_income, '$', locale="en_US")
    total_expense = index["total_expense"]
    total_expense_format = babel.numbers.format_currency(total_expense, '$', locale="en_US")
    result = index["result"]
    result_format = babel.numbers.format_currency(result, '$', locale="en_US")

    # get list of incomeson this plan
    incomes = db.execute("SELECT * FROM incomes WHERE user_id = ? AND plan_id=? ORDER BY id ASC", user_id, plan_id)
    
    # get list of expenses on this plan inner join types of expenses
    expenses = db.execute("SELECT * FROM expenses WHERE user_id = ? AND plan_id=? ORDER BY name ASC", user_id, plan_id)

    # get list of types of expenses for entering new 
    types_of_expenses = db.execute("SELECT name FROM types_of_expenses WHERE user_id=?;", user_id)


    if request.method == "POST":
        
        # GET PLAN NAME
        new_plan_name = request.form.get("plan_name")
        
        # GET INCOMES
        income_name = request.form.get("income_name")
        currency = request.form.get("currency")
        income = request.form.get("income") 
        income_to_delete = request.form.get("income_to_delete")

        rows = db.execute("SELECT * FROM incomes WHERE user_id = :user_id AND plan_id = :plan_id AND name = :name",
                            user_id=user_id,
                            plan_id=plan_id,
                            name=income_name)

        # Ensure income name not taken
        if len(rows) != 0:
            flash(u'Please provide other Income Name. This name has already been taken', 'error')
            return render_template("edit_plan.html", plans=plans, plan_name=plan_name, 
                                            plan_id=plan_id, PERIOD=PERIOD, 
                                            expenses=expenses, types_of_expenses=types_of_expenses,
                                            currencies=currencies, incomes=incomes, total_income_format=total_income_format,
                                            total_expense_format=total_expense_format, result_format=result_format)

        # GET EXPENSES
        expense_name = request.form.get("expense_name")
        expense = request.form.get("expense")
        expense_to_delete = request.form.get("expense_to_delete")


        if new_plan_name != plan_name:
            db.execute('UPDATE plans SET name=:new_plan_name WHERE user_id = :user_id AND id = :plan_id', 
                        new_plan_name=new_plan_name, user_id=user_id, plan_id=plan_id)
            flash("Name Update succesfully")


        # Add new INCOME to plan 
        if income_name and income:
            
            # update plans database with this plans id
            
            total_income = int(total_income) + int(income)
            result = int(result) + int(income)

          
        
            # INSERT incomes database with this plans id
            db.execute("INSERT INTO incomes (day_added, name, user_id, currency, income, plan_id) VALUES (:day_added, :name, :user_id, :currency, :income, :plan_id)",
                day_added=now,
                name=income_name,
                user_id=user_id,
                currency=currency,
                income=income,
                plan_id=plan_id) 


            db.execute("UPDATE plans SET total_income=:total_income, result=:result WHERE user_id = :user_id AND id = :plan_id",
                        total_income=total_income,
                        result=result,
                        user_id=user_id,
                        plan_id=plan_id)
            flash("Income Added Successfully! Plan result and Total Income updated.")

        elif income is None:
            flash("Please fill out income field.")
        elif income_name is None:
            flash("Please fill out income name field.")
        elif plan_name is None and expense_name is None and expense is None:
            flash("Please fill out all fields")

        # Delete income from plan 
        if income_to_delete:
            amount_income_to_delete = db.execute("SELECT income FROM incomes WHERE name =:income_to_delete AND user_id = :user_id AND plan_id = :plan_id",
                                                income_to_delete=income_to_delete,
                                                user_id=user_id,
                                                plan_id=plan_id)

            index = amount_income_to_delete[0]
            total_income = total_income - int(index["income"])
            result = int(result) - int(index["income"])

            # delete from table
            db.execute('DELETE FROM incomes WHERE name=:income_to_delete AND plan_id =:plan_id', 
                        income_to_delete=income_to_delete,
                        plan_id=plan_id)
            
            # update total income on plans table
            db.execute('UPDATE plans SET total_income = :total_income, result = :result WHERE user_id=:user_id AND id=:plan_id',
                        total_income=total_income,
                        result=result,
                        user_id=user_id,
                        plan_id=plan_id)

            flash("Income Deleted Successfully")



        # Add new EXPENSE to plan
        if expense_name and expense:
            
            # update plans database with this plans id
            total_expense = int(total_expense) + int(expense)
            result = int(result) - int(expense)
            
            # INSERT expenses database with this plans id
            
            db.execute("INSERT INTO expenses (day_added, name, user_id, expense, plan_id) VALUES (:day_added, :name, :user_id, :expense, :plan_id)",
                day_added=now,
                name=expense_name,
                user_id=user_id,
                expense=expense,
                plan_id=plan_id) 

            # update total expense on plans table
            db.execute('UPDATE plans SET total_expense = :total_expense, result = :result WHERE user_id=:user_id AND id=:plan_id',
                        total_expense=total_expense,
                        result=result,
                        user_id=user_id,
                        plan_id=plan_id)

            flash("Expense Added Successfully! Plan result and Total Income updated.")

        # Check for expense input fields 
        elif expense is None:
            flash("Please fill out expense field.")
        elif income_name is None:
            flash("Please fill out expense name field.")
        elif plan_name is None and expense_name is None and expense is None:
            flash("Please fill out all fields")
        
        # Delete expense from plan 
        if expense_to_delete:
            amount_expense_to_delete = db.execute("SELECT expense FROM expenses WHERE name = :expense_to_delete AND user_id=:user_id AND plan_id = :plan_id",
                                                expense_to_delete=expense_to_delete,
                                                user_id=user_id,
                                                plan_id=plan_id)

            index = amount_expense_to_delete[0]
            total_expense = total_expense - int(index["expense"])
            result = int(result) + int(index["expense"])

            # delete from table
            db.execute('DELETE FROM expenses WHERE name=:expense_to_delete', 
                        expense_to_delete=expense_to_delete)
            
            # update total expense on plans table
            db.execute('UPDATE plans SET total_expense = :total_expense, result=:result WHERE user_id=:user_id AND id=:plan_id',
                        total_expense=total_expense,
                        result=result,
                        user_id=user_id,
                        plan_id=plan_id)

            flash("Expense Deleted Successfully")

        
        return redirect(request.url)

    return render_template("edit_plan.html", plans=plans, plan_name=plan_name, 
                                            plan_id=plan_id, PERIOD=PERIOD, 
                                            expenses=expenses, types_of_expenses=types_of_expenses,
                                            currencies=currencies, incomes=incomes, total_income_format=total_income_format,
                                            total_expense_format=total_expense_format, result_format=result_format)





@app.route("/new_plan", methods=["GET", "POST"])
@login_required
def new_plan():

    
    # get user id to pass as a list to html 
    user_id = session["user_id"]
    name = db.execute("SELECT name FROM users WHERE id = ?", user_id)
    latest_currency = ""

    plan_id_index = db.execute("SELECT id FROM plans WHERE user_id = ? ORDER BY id DESC limit 1", user_id)
    
    if len(plan_id_index) != 0:
        index = plan_id_index[0]
        plan_id = index["id"]

        # get latest currency
        currency_index = db.execute("SELECT currency FROM incomes WHERE user_id = ? AND plan_id = ? ORDER BY plan_id DESC limit 1", user_id, plan_id)
        index = currency_index[0]
        latest_currency= index["currency"]   

    # create plan ID by executing a query over plas and past ids
    past_id = db.execute("SELECT id FROM plans WHERE user_id=? ORDER BY id DESC limit 1", user_id)
    
    #checking if it´s the first plan for this user
    if past_id:
        index = past_id[0]
        plan_id = index["id"] + 1
    else: 
        plan_id = 1

    #get time on real time
    now = date.today()

    # get list of types of expenses for entering new 
    types_of_expenses = db.execute("SELECT name FROM types_of_expenses WHERE user_id=?;", user_id)

        
    if request.method == "POST":
        
        PERIOD = 0
        
        # PERIOD DEFINITION
        if request.form.get("periods") == "Day":
            # calculate today and send it to template
            PERIOD = now.strftime("%A %d, %b of %Y")
            
        if request.form.get("periods") == "Month":
            # calculate 1 month from today and send it to template
            this_month = now.strftime("%Y-%m-%d")
            next_month = (pd.to_datetime(this_month)+pd.DateOffset(months=1)).strftime("%Y-%m-%d")
            PERIOD = f"1 Month. \nFrom: {this_month} to {next_month}"

        if request.form.get("periods") == "Quarter":
            # calculate 3 months from today and send it to template
            this_month = now.strftime("%Y-%m-%d")
            next_month = (pd.to_datetime(this_month)+pd.DateOffset(months=3)).strftime("%Y-%m-%d")
            PERIOD = f"1 quarter. \nFrom: {this_month} to {next_month}"
            
        if request.form.get("periods") == "Year":
            # calculate 12 month from today and send it to template
            this_month = now.strftime("%Y-%m-%d")
            next_month = (pd.to_datetime(this_month)+pd.DateOffset(months=12)).strftime("%Y-%m-%d")
            PERIOD = f"1 year. \nFrom: {this_month} to {next_month}"

        # get plan name   
        plan_name = request.form.get("plan_name")

        # INCOME
        
        # get input from income form
        income_name = request.form.get("income_name")
        currency = request.form.get("currency")
        income = request.form.get("income")

        

        total_income = 0
        total_expense = 0

        # checking if income is none
        if income:
            total_income = int(income)
        else:
            total_income = 0

        # EXPENSES

        # get input from expense form
        expense_name1 = request.form.get("expense_name1")
        expense_name2 = request.form.get("expense_name2")

        expense1 = request.form.get("expense1")
        expense2 = request.form.get("expense2")

        # Check which fields have values
        if expense1:
            total_expense = total_expense + int(expense1)
            if expense2:
                total_expense = total_expense + int(expense2)
        elif expense2:
            total_expense = total_expense + int(expense2)


        # Calculate Result
        result = total_income - total_expense


        # DATABASE INSERTS

        # insert income into incomes table
        db.execute("INSERT INTO incomes (day_added, name, user_id, currency, income, plan_id) VALUES (:day_added, :name, :user_id, :currency, :income, :plan_id)",
                    day_added=now,
                    name=income_name,
                    user_id=user_id,
                    currency=currency,
                    income=total_income,
                    plan_id=plan_id) 
        
        # insert expense 1 into expenses table
        if expense1:  
            db.execute("INSERT INTO expenses (day_added, name, user_id, plan_id, expense) VALUES (:day_added, :name, :user_id, :plan_id, :expense)",
                        day_added=now,
                        name=expense_name1,
                        user_id=user_id,
                        plan_id=plan_id,
                        expense=expense1) 
        
        if expense2:
            # insert expense 2 into expenses table
            db.execute("INSERT INTO expenses (day_added, name, user_id, plan_id, expense) VALUES (:day_added, :name, :user_id, :plan_id, :expense)",
                        day_added=now,
                        name=expense_name2,
                        user_id=user_id,
                        plan_id=plan_id,
                        expense=expense2)               

        #insert into database new plan
        prim_key = db.execute("INSERT INTO plans (id, day_added, name, period, total_income, total_expense, result, user_id) VALUES (:id, :day_added, :name, :period, :total_income, :total_expense, :result, :user_id)",
                                id=plan_id,
                                day_added=now,
                                name=plan_name,
                                period=PERIOD,
                                total_income=total_income,
                                total_expense=total_expense,
                                result=result,
                                user_id=user_id)

        #Check for error in uploading into plans database
        if prim_key is None:
            flash("Error. Please contact support")
            return redirect("/new_plan")
        else:
            flash("Plan added! Chek out your plans on the Plans Page.")   

        
        return redirect("/")

    return render_template("new_plan.html", name=name, currencies=currencies, 
    types_of_expenses=types_of_expenses, periods=periods, plan_id=plan_id, 
    latest_currency=latest_currency) 



@app.route("/add_expense", methods=["GET", "POST"])
@login_required
def add_expense():
    
    user_id = session["user_id"]
    name = db.execute("SELECT name FROM users WHERE id = ?", user_id)
    latest_currency = ""
    
    # Get latest plan_id
    plan_id_index = db.execute("SELECT id FROM plans WHERE user_id = ? ORDER BY id DESC limit 1", user_id)
    
    if len(plan_id_index) != 0:
        index = plan_id_index[0]
        plan_id = index["id"]

        # get latest currency
        currency_index = db.execute("SELECT currency FROM incomes WHERE user_id = ? AND plan_id = ? ORDER BY plan_id DESC limit 1", user_id, plan_id)
        index = currency_index[0]
        latest_currency= index["currency"]

    types_of_expenses = db.execute("SELECT * FROM types_of_expenses WHERE user_id = ?", user_id)

    if request.method == "POST":

        expense_name = request.form.get("ExpenseName")
        expense_desc = request.form.get("ExpenseDescription")

        if not expense_name:
            flash(u'Must provide an Expense Name', 'error')
            return redirect("add_expense")

        
        date_time = date.today()

        
        # if description is not null:
        if expense_desc is not None:
            prim_key = db.execute("INSERT INTO types_of_expenses (day_added, name, description, user_id) VALUES (:day_added, :name, :description, :user_id)",
                                  day_added=date_time,
                                  name=expense_name,
                                  description=expense_desc,
                                  user_id=user_id)

            if prim_key is None:
                flash("Error. Please contact support")
                return redirect("/new_plan")
                
            flash(u'Expense  Added!')

        elif not expense_desc:
            prim_key = db.execute("INSERT INTO types_of_expenses (day_added, name, user_id) VALUES (:day_added, :name, :user_id)",
                                  day_added=date_time,
                                  name=expense_name,
                                  user_id=user_id)

            if prim_key is None:
                flash("Error. Please contact support")
                return redirect("/add_expense")   

            flash(u'Expense  Added!')    

        return redirect("/add_expense")

    return render_template("add_expense.html", types_of_expenses=types_of_expenses, latest_currency=latest_currency, name=name)


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

        flash("Welcome to Personances! Here you will be able to manage your personal finances.")

        return redirect("/")

    else:
        return render_template("register.html", type_of_user= type_of_user, expertise=expertise)

@app.route("/taxes", methods=["GET", "POST"])
@login_required
def taxes():
    if request.method == "GET":

        # show list of taxes
        user_id = session["user_id"]

        taxes = db.execute("SELECT * FROM taxes_per_user WHERE user_id = ?", user_id)
        
        return render_template("taxes.html", taxes=taxes)

    return render_template("new_tax.html") 


