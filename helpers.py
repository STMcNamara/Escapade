import requests

from flask import redirect, render_template, request, session
from functools import wraps
from datetime import datetime, date


def apology(message, code=400):
    """Render message as an apology to user."""
    return render_template("apology.html", message=message, code=code)

def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/0.12.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def sessionActive():
    """
    Checks if there is an active user session and returns True or False
    """
    if session.get("user_id") is None:
        return False
    else:
        return True

def validFlightSearchQuery(queryList,ss_places):
    """
    Performs data validation checks on user generated queries for the ss API
    endpoint:
        Dates: Confirms that the outbound date is in the future, and that the return
        date/time is later than the outbound.

        Destinations: Confirms that the origin and destination places are the valid
        list of places for a live_search query, defined within ss_places.

    (In theory these should be picked up at the front end, but this provides a
    serverside backup in case of omissions, for security, and for development
    purposes in the absence of front end validation)

    Args:
        queryList(list(of dictionaries)): A list of dictionaries, each containing keys
        required to construct an URL for the Live Flight Search API endpoint.

        validPlaces(list(of dictionaries)): A list of dictionaries defining the 
        attributes for a place used by the SkyScanner API.

    Returns:
        validQuery(Bool): Returns True if validation conditions are met. Raises errors
        otherwise.

    Exceptions:
        Raises assetion error on invalid data with descriptive message
    """

    for query in queryList:
        # Check outbound date not before today
        outboundDate = datetime.strptime(query["outboundpartialdate"],"%Y-%m-%d").date()
        assert outboundDate >= date.today(),"Outbound date occurs in the past"

        # If there is an inbound trip, check it occurs after or equal to outbound
        try:
            inboundDate = datetime.strptime(query["inboundpartialdate"], "%Y-%m-%d").date()
        except:
            inboundDate = None

        if not inboundDate == None:
            assert inboundDate >= outboundDate, "Inbound date cannot be before outbound"

        # Define the list of valid places (for now, airport codes)
        validPlaces = []
        for place in ss_places:
            validPlaces.append(place['PlaceId'])

        # Check that origin and destination places are on the valid list
        assert query['originplace'] in validPlaces, "Origin place not on valid places list"
        assert query['destinationplace'] in validPlaces, "Destination place not on valid places list"

    return True

def possibleTravelDates():
    """
    TODO
    """
