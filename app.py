from flask import Flask, abort, redirect, render_template, request
from ss_api_functions import formatBqUrl, BrowseQuotes

# Configure application
app = Flask(__name__)

# Define default values - TODO to be replaced by database and/or user defined parameters
country = 'US' # User's skyscanner home country
currency = "USD" # User's skyscanner currency
locale = 'en-US' # User's skyscanner locale

@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    """Placeholder for home page)"""
    return render_template("index.html")

@app.route("/search_bq", methods=["GET", "POST"])
def search_bq():
    """
    GET: Presents search_bq.html to allow user to input queries.
    POST: Reads user inputs and number of queries requested. Formats URL and passes
    to BrowseQuotes. Returns results as results_bq.html, providing the single
    cheapest matching result for each individual query.
    """
    # Reached via POST (form submitted)
    if request.method == "POST":
    # Populate query dictionary with default location and form parameters
        rows = int(request.form.get("rowNum"))
        print(rows)
        queryList = []
        for i in range(rows+1):
            queryList.append({'country' : country, 'currency': currency, 'locale' : locale,
                        'originplace': request.form.get("originplace_" + str(i)),
                        'destinationplace': request.form.get("destinationplace_" + str(i)),
                        'outboundpartialdate': request.form.get("outboundpartialdate_" + str(i))})
        print(queryList)
        # Produce URL string for BrowseQuotes call
        query_URL = formatBqUrl(queryList)
        print(query_URL)
        # Call BrowseQuotes and return list of dictionaries - CURRENTLY 1 ITEM
        resultsDict = BrowseQuotes(query_URL)
        print(resultsDict)
        return render_template("results_bq.html", resultsDict=resultsDict)

    # Reached via GET (display form)
    else:
        return render_template("search_bq.html")

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
    """TODO - Placeholder for accounts functionality - Log Out"""
    return render_template("todo.html")

@app.route("/login")
def login():
    """TODO - Placeholder for accounts functionality - Log In"""
    return render_template("todo.html")
