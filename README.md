# Personances (Peronsonal Finances)
#### Video Demo:  https://youtu.be/NXgBkeQX7zc

#### Description: Perosonances is a Flask-base web app that lets you manage your personal finance by creating and editing plans over periods of time.

#### This idea comes from my need to organize my personal finances on the day to day. I will use it and my family also to organize better and create plans for the future. 

#### I used some of pset09s user login/registration basic app.py data for easy management, and focused on creating new pages for this managing app.
#### I focused on the creation of the database for easy access and easy UI, without too much javascript. 
#### used jinja expresions to easy visualize variables over the web page, and concentrated also on reviewing all paths the user takes on creating new plans and managing incomes and expenses. 
#### DEPENDENCIES: Note that there are varius libraries that need to be installed previously executing the app. 

#### app.py is the main code for the app to run. It containts all the functions for the directories and pages of the webpage. All of it is made by me, it has some content that i searched for it online, buy everything adapted to my requirements and my app. It has a lot of database executions, logic in terms of numeric operations and validations for user input. 

#### /templates is the directory for all .html templates. The one that took me the most was edit plan because of all the forms and validations i needed. And the other one that took me a lot was index, that shows the Dashboard. I had to teach myself javascript to understand the Google Charts code and adapt it to what i wanted. 

#### A difficult task I had was to convert the db.execute cs50 function values to what i needed. After reaserch on tuples, lists and dictionaries, I could finnally do it and pass the data to javascript using jinja notations. 

#### styles.css was a challenge also, as I had to do a lot of reaserch on all the functions that could be called to give the page a little bit of art and feeling. The fact that it is mainly forms, i used botstrap for forms and buttons. 

#### extras.py is used the cs50 pst09 login required decorator (#shoutout) because it is very usefull to check for the session's user_id and login on every page. I also used the session[] to add values to it and verify later. Very usefull.

#### static. User a webpage called logomaker.com to make the personalized Personasnes logo. 

