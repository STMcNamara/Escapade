"""
This file manages the hosting and navigation of the Escapade webpage via
the flask framework. It also conducts intermediary formatting and information
transfer between the html/js front end, helper functions backend, and the
Escapade database.
"""

import os
from flask import Flask, abort, redirect, render_template, request, session
from pathlib import Path
from ss_api_functions import formatBqUrl, BrowseQuotes, CSVtoDict, liveSearchRequestQuotes_T
from db_functions import db_intialise, db_connect,db_createUser
from helpers import apology
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cashed
@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Define datebase name, and if required create or update
db = r"database.db"
db_intialise(db)


# Define default values - TODO to be replaced by database and/or user defined parameters
country = 'UK' # User's skyscanner home country
currency = "GBP" # User's skyscanner currency
locale = 'en-GB' # User's skyscanner locale
adults = '1' # Number of adults to search for

# PLACEHOLDER - Load SKyscanner places into dictionary for use in html forms
ss_places_csv = './data/results_places.csv'
ss_places = CSVtoDict(ss_places_csv)


@app.route("/")
def index():
    """Placeholder for home page"""
    return render_template("index.html")

@app.route("/search_bq", methods=["GET", "POST"])
def search_bq():
    """
    GET:
        Presents search_bq.html to allow user to input queries.

    POST:
        INPUTS:
            Reads user inputs from search_bq.html via request.form.get (where N
            is the number of query rows):
                originplace_[0-N] (string): In the format Skyscanner PlaceId
                destination_[0-N] (string): In the format Skyscanner PlaceId
                outboundpartialdate_[0-N] (string): In the html date format yyyy-mm-dd
            TODO - placeholder - uses the globals country, currency and locale

        CALLS:
            Passes data to formatBqUrl and BrowseQuotes in ss_api_functions.py

        RETURNS:
            results_bq.html consisting of an automatically generated table
            that contains the query results where:
                resultsDict (list(of dictionaries)): From BrowseQuotes
    """
    # Reached via POST (form submitted)
    if request.method == "POST":
    # Populate query dictionary with default location and form parameters
        rows = int(request.form.get("rowNum"))
        queryList = []
        for i in range(rows+1):
            queryList.append({'country' : country, 'currency': currency, 'locale' : locale,
                        'originplace': request.form.get("originplace_" + str(i)),
                        'destinationplace': request.form.get("destinationplace_" + str(i)),
                        'outboundpartialdate': request.form.get("outboundpartialdate_" + str(i))})

        # Produce URL string for BrowseQuotes call
        query_URL = formatBqUrl(queryList)
        # Call BrowseQuotes and return list of dictionaries - CURRENTLY 1 ITEM
        resultsDict = BrowseQuotes(query_URL)
        return render_template("results_bq.html", resultsDict=resultsDict)

    # Reached via GET (display form)
    else:
        return render_template("search_bq.html", ss_places=ss_places)

@app.route("/search_live", methods=["GET", "POST"])
def search_live():
    """
    GET:
        Presents search_live.html to allow user to input queries.

    POST:
        INPUTS:
            Reads user inputs from search_bq.html via request.form.get (where N
            is the number of query rows):
                originplace_[0-N] (string): In the format Skyscanner PlaceId
                destination_[0-N] (string): In the format Skyscanner PlaceId
                outboundpartialdate_[0-N] (string): In the html date format yyyy-mm-dd
                inbounddate_[0-N] (string): Optional, yyyy-mm-dd
            TODO - placeholder - uses the globals country, currency, locale and adults

            CALLS:
                Passes data to liveSearchRequestQuotes in ss_api_functions.py

            RETURNS:
                results_live.html consisting of an automatically generated table
                that contains the query results where:
                    resultsDict (list(of dictionaries)): From Live Search
    """
    # Reached via POST (form submitted)
    if request.method == "POST":
    # Populate query dictionary with default location and form parameters
        rows = int(request.form.get("rowNum"))
        queryList = []
        for i in range(rows+1):
            queryList.append({'country' : country, 'currency': currency, 'locale' : locale, 'adults' : adults,
                        'originplace': request.form.get("originplace_" + str(i)),
                        'destinationplace': request.form.get("destinationplace_" + str(i)),
                        'outboundpartialdate': request.form.get("outboundpartialdate_" + str(i)),
                        'inbounddate': request.form.get("inbounddate_" + str(i))})

        # Make the live search request
        resultsDict = liveSearchRequestQuotes_T(queryList)
        return render_template("results_live.html", resultsDict=resultsDict)

    # Reached via GET (display form)
    else:
        return render_template("search_live.html", ss_places=ss_places)






@app.route("/register", methods=["GET", "POST"])
def register():
    """TODO - Allows the user to register an account and provde Optional
    account details.

    GET:
        Presents register.html to allow user to submit account details.

    POST:
        INPUTS - TODO

        CALLS - TODO

        RETURNS - TODO

    """
    # User reached route via POST (by submitting account details)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match")

        # Hash the password and create temporary variables
        hash = generate_password_hash(request.form.get("password"))

        # Create user object from form parameters
        user = (request.form.get("username"),
                hash,
                request.form.get("firstName"),
                request.form.get("secondName"),
                request.form.get("email"),
                "","","")

        # Connect to database and insert user data
        result = db_createUser(db,user)

        if not result:
            return apology("User already exists")

        # TODO - for now return to front page
        return render_template("index.html")

    else:
        return render_template("register.html")

@app.route("/password")
def password():
    """TODO - Placeholder for accounts functionality - password Change"""
    return render_template("todo.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """TODO - Placeholder for accounts functionality - Log In"""

    # Forget any user_id
    # session.clear()

    # User reached route via POST (as by submitting )
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        else:
            return render_template("todo.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """TODO - Placeholder for accounts functionality - Log Out"""
    return render_template("todo.html")
