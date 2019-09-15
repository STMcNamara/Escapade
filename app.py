from flask import Flask, abort, redirect, render_template, request

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
    """Handle requests for / via GET (and POST)"""
    return render_template("index.html")

@app.route("/search_bq", methods=["GET", "POST"])
def search_bq():
    """Input a BrowseQuotes query and get a response"""

    # Reached via POST (form submitted)
    # NOT NOW - RETURN TODO
    if request.method == "POST":
        return render_template("todo.html")

    # Reached via GET (display form)
    else:
        return render_template("search_bq.html")
