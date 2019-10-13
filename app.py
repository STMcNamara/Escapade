"""
This file manages the hosting and navigation of the Escapade webpage via
the flask framework. It also conducts intermediary formatting and information
transfer between the html/js front end, helper functions backend, and the
Escapade database.
"""

from flask import Flask, abort, redirect, render_template, request
from pathlib import Path
from ss_api_functions import formatBqUrl, BrowseQuotes, CSVtoDict, liveSearchRequestQuotes

# Configure application
app = Flask(__name__)

# Define default values - TODO to be replaced by database and/or user defined parameters
country = 'UK' # User's skyscanner home country
currency = "GBP" # User's skyscanner currency
locale = 'en-GB' # User's skyscanner locale
adults = '1' # Number of adults to search for

# PLACEHOLDER - Load SKyscanner places into dictionary for use in html forms
ss_places_csv = './data/results_places.csv'
ss_places = CSVtoDict(ss_places_csv)


@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

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
            TODO - placeholder - uses the globals country, currency, locale and adults
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
                        'outboundpartialdate': request.form.get("outboundpartialdate_" + str(i))})

        # Make the live search request
        resultsDict = liveSearchRequestQuotes(queryList)
        return render_template("results_live.html", resultsDict=resultsDict)

    # Reached via GET (display form)
    else:
        return render_template("search_live.html", ss_places=ss_places)


@app.route("/password")
def password():
    """TODO - Placeholder for accounts functionality - password Change"""
    return render_template("todo.html")

@app.route("/logout")
def logout():
    """TODO - Placeholder for accounts functionality - Log Out"""
    return render_template("todo.html")

@app.route("/register")
def register():
    """TODO - Placeholder for accounts functionality - Register"""
    return render_template("todo.html")

@app.route("/login")
def login():
    """TODO - Placeholder for accounts functionality - Log In"""
    return render_template("todo.html")
