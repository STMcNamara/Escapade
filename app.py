from flask import Flask, abort, redirect, render_template, request
from ss_api_functions import formatBqUrl, BrowseQuotes

# Configure application
app = Flask(__name__)

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
    Input a BrowseQuotes query (list of dictionaries and get a response)
    CURRENTLY ONLY TAKES A SINGLE TRIP NEED TO FIGURE OUT BEST FORMAT FOR MULTIPLE
    """
    # Reached via POST (form submitted)
    if request.method == "POST":
    # Populate query dictionary with default location and form parameters
        queryDict = [{'country' : 'US', 'currency': 'USD', 'locale' : 'en-US',
                    'originplace': request.form.get("originplace"),
                    'destinationplace': request.form.get("destinationplace"),
                    'outboundpartialdate': request.form.get("outboundpartialdate")}]

        # Produce URL string for BrowseQuotes call
        query_URL = formatBqUrl(queryDict)

        # Call BrowseQuotes and return list of dictionaries - CURRENTLY 1 ITEM
        resultsDict = BrowseQuotes(query_URL)

        return render_template("results_bq.html", outboundpartialdate=queryDict[0]['outboundpartialdate'],
                                originplace=queryDict[0]['originplace'],
                                destinationplace=queryDict[0]['destinationplace'],
                                MinPrice=resultsDict[0]['MinPrice'],
                                Carrier=resultsDict[0]['Outbound_CarrierID'])

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
