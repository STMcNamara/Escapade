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
