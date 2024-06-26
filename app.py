"""
This file manages the hosting and navigation of the Escapade webpage via
the flask framework. It also conducts intermediary formatting and information
transfer between the html/js front end, helper functions backend, and the
Escapade database.
"""

import os
from flask import Flask, abort, redirect, render_template, request, session
from pathlib import Path
from ss_api_functions import BrowseQuotes, BrowseQuotesFormatResults, CSVtoDict 
import db_functions
from helpers import sessionActive,login_required,apology,validFlightSearchQuery
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
db = r"escapade.db"
db_functions.intialise(db)


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
                inboundpartialdate_[0-N] (string): In the html date format yyyy-mm-dd
            TODO - placeholder - uses the globals country, currency and locale

        CALLS:
            Passes data to BrowseQuotes in ss_api_functions.py

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
        
        # For each combination of destination and dates
        for i in range(rows+1):
            # Populate list of Origin places and Destination places
            originplacesList = request.form.getlist("originplaces_" + str(i))
            destinationplacesList = request.form.getlist("destinationplaces_" + str(i))
            
            # Populate list of outbound and inbound dates
            outboundpartialdateString = request.form.get("outboundpartialdate_" + str(i))
            inboundpartialdateString = request.form.get("inboundpartialdate_" + str(i))

            outboundpartialdateList = outboundpartialdateString.split(",")
            inboundpartialdateList = inboundpartialdateString.split(",")
            
            # Format multi-data lists into individual date and place itineraries and append to list
            for originplace in originplacesList:
                for destinationplace in destinationplacesList:
                    for outboundDate in outboundpartialdateList:
                        for inboundDate in inboundpartialdateList:
                            queryList.append({'country' : country, 'currency': currency, 'locale' : locale, 'adults' : adults,
                            'originplace': originplace,
                            'destinationplace': destinationplace,
                            'outboundpartialdate': outboundDate,
                            'inboundpartialdate': inboundDate})
       
        # Check search query values are valid - Raises error if not
        validFlightSearchQuery(queryList, ss_places)

        # Store the query  in the database before calling (to record timestamp)
        if sessionActive():
            user_id = session["user_id"]
        else:
            user_id = ""
        
        search_id = db_functions.logBQQuery(db, user_id, queryList)  

        # Call the Browse Quotes API endpoint and retreive raw results
        results_json = BrowseQuotes(queryList)
        
        # Store the result in the database
        db_functions.logBQResults(db, user_id, search_id, results_json) 
        
        # Format the results for interpretation be the return form
        resultsDict = BrowseQuotesFormatResults(results_json)
        
        return render_template("results_bq.html", resultsDict=resultsDict)

    # Reached via GET (display form)
    else:
        return render_template("search_bq.html", ss_places=ss_places)


@app.route("/search_live2", methods=["GET", "POST"])
def search_live2():
    """
    GET:
        Presents search_live2.html to allow user to input queries.

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

        DATABASE:
            Stores the search query, raw results and formatted results in the
            database.
    """
    # Reached via POST (form submitted)
    if request.method == "POST":
    # Populate query dictionary with default location and form parameters
        rows = int(request.form.get("rowNum"))
        queryList = []
        
        # For each combination of destination and dates
        for i in range(rows+1):
            # Populate list of Origin places and Destination places
            originplacesList = request.form.getlist("originplaces_" + str(i))
            destinationplacesList = request.form.getlist("destinationplaces_" + str(i))
            
            # Populate list of outbound and inbound dates
            outboundpartialdateString = request.form.get("outboundpartialdate_" + str(i))
            inbounddateString = request.form.get("inbounddate_" + str(i))

            outboundpartialdateList = outboundpartialdateString.split(",")
            inbounddateList = inbounddateString.split(",")
            
            # Format multi-data lists into individual date and place itineraries and append to list
            for originplace in originplacesList:
                for destinationplace in destinationplacesList:
                    for outboundDate in outboundpartialdateList:
                        for inboundDate in inbounddateList:
                            queryList.append({'country' : country, 'currency': currency, 'locale' : locale, 'adults' : adults,
                            'originplace': originplace,
                            'destinationplace': destinationplace,
                            'outboundpartialdate': outboundDate,
                            'inbounddate': inboundDate})



        # Return the results to the user
        return render_template("results_live.html", resultsDict={})
        

    # Reached via GET (display form)
    else:
        return render_template("search_live2.html", ss_places=ss_places)

@app.route("/search_history", methods=["GET", "POST"])
@login_required
def search_history():
    """
    GET:
        Presents search_history.html to the user to view their search history
        with the option to re-run past searches, or view past results.

        Builds the search history table with data and fields from the
        search_bq_log database, with form submission names links to search_ids.

    POST - "rerun":
        INPUTS:
            Using the search_id submitted with the POST form, retreives the
            associated search parameters from the database to duplicate a
            search_bq query.

        CALLS:
            Passes data to BrowseQuotes in ss_api_functions.py

        RETURNS:
            results_bq.html consisting of an automatically generated table
            that contains the query results where:
                resultsDict (list(of dictionaries)): From Browse Quotes

        DATABASE:
            Stores the search query, raw results and formatted results in the
            database.

    POST - "view_results"  :
        INPUTS:
            Using the search_id submitted with the POST form, retreives the
            associated raw search results.

        CALLS:
            Formats the raw results from the database using BrowseQuotesFormatResults
            in ss-ss_api_functions.py.

        RETURNS:
            results_bq.html consisting of an automatically generated table
            that contains the query results where:
                resultsDict (list(of dictionaries)): Formatted from results
                retreived from the database.

        DATABASE:
            N/A: Makes no changess
    """
    if request.method == "POST":

        #If rerun logic selected
        if "rerun" in request.form:

            # Get the search ID
            search_id = request.form.get("rerun")

            # Retrieve the search query to rerun
            queryList = db_functions.getSearchQuery(db, search_id)

            # Check search query values are valid - Raises error if not
            validFlightSearchQuery(queryList, ss_places)

            # Store the query  in the database before calling (to record timestamp)
            if sessionActive():
                user_id = session["user_id"]
            else:
                user_id = ""
            
            search_id = db_functions.logBQQuery(db, user_id, queryList)  

            # Call the Browse Quotes API endpoint and retreive raw results
            results_json = BrowseQuotes(queryList)
            
            # Store the result in the database
            db_functions.logBQResults(db, user_id, search_id, results_json) 

            # Format the results for interpretation be the return form
            resultsDict = BrowseQuotesFormatResults(results_json)

        # If retreive results selected on POST
        else:
            # Get the search ID
            search_id = request.form.get("view_results")

            # Retreive the raw historic results for the search-id from the database
            results_json = db_functions.getSearchResult(db, search_id)

            # Format the results for interpretation be the return form
            resultsDict = BrowseQuotesFormatResults(results_json)

        # Return the results to the user
        return render_template("results_bq.html", resultsDict=resultsDict)

    else:
        #For GET - Retreive the user's search history from the database
        userSearchHistory = db_functions.getUserSearchHistory(db, session["user_id"])

        return render_template("search_history.html", searchHistory=userSearchHistory)


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Allows the user to register an account with username and password
    and provde optional account details.

    GET:
        Presents register.html to allow user to submit account details.

    POST:
        INPUTS:
            Reads user parameters from register.html, and conducts basic
            validation:
                username(string): Required
                password(string): Required
                confirmation(string): Required - must match password
                firstName(string): Optional
                secondName(string): Optional
                email(string): Optional

        CALLS:
            generate_password_hash to hash the password

            db_createUser to confirm username does not exist, and write user
            information to the database

        RETURNS:
            On success, returns the user to index.html (currently does not log in.
            On failure returns apology with the appropriate data validation
            information.

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
        result = db_functions.createUser(db,user)

        if not result:
            return apology("User already exists")

        else:
            # Update user to retreive generated data (user_id)
            user = db_functions.getUser(db, request.form.get("username"))
            
            # Leave the user logged in and return to index
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
        
            return render_template("index.html")

    else:
        return render_template("register.html")

@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """
    Allows the user to change password
    """
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Retreive the user object from the database
        user = db_functions.getUser(db, session["username"])

        # Check inputted password against hash
        if not check_password_hash(user["password"], request.form.get("current_password")):
            return apology("incorrect password")

        # Ensure new password was submitted
        elif not request.form.get("new_password"):
            return apology("must provide new password")

        # Ensure passwords match
        elif request.form.get("new_password") != request.form.get("confirmation"):
            return apology("passwords do not match")

        # Hash the new password
        hash = generate_password_hash(request.form.get("new_password"))

        # Update the hash in the database
        db_functions.updatePassword(db, hash, session["username"])

        # Redirect the user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("password.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Allows the user to log in and creates a user session

    GET:
        Presents login.html to allow use to submit login information

    POST:
        INPUTS:
            Reads the user login parameters, and conducts basic validation:
                username(string): Required
                password(string): Required

        CALLS:
            db_getUser to retreive user details from the database

            check_password_hash to confirm passwords match

        RETURNS:
            On success, returns the user to index.html. Logs the user in by adding
            user_id and unsername to the session dictionary.
            On failure returns apology with the appropriate data validation
            information.
    """

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

        # Retreive the user object from the database
        user = db_functions.getUser(db, request.form.get("username"))

        # Check if user exists
        if not user:
            return apology("User does not exist", 403)

        # Check the password is correct
        if not check_password_hash(user["password"], request.form.get("password")):
            return apology("Incorrect password", 403)

        else:
            # Create a session
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]

            return render_template("index.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    """
    Logs user out by clearing all information from the session dictionary

    RETURNS:
        Returns the user to index.html

    """

    # Clear session database
    session.clear()

    # Redirect user to login form
    return redirect("login")
