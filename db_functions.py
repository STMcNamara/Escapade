"""
This file contains all functions that directly interact with the Escapade
database. This is includes, connecting, creation of tables, reading, writing,
and interpratation and manipulation of raw data into a format suitable for
sqlite3.
"""


import sqlite3
from sqlite3 import Error
import json
from datetime import datetime


""" Generic database helpers:"""

def db_connect(db_file):
    """
    Create a connection object to the database. If no database exists, will
    create that database

    Args:
        db_file(string): The address of the database file to be connected to

    Returns:
        conn(object): The database connection object, or none

    Exceptions:
        e(string): An sqlite3 error message upon failure to connect to a database
        """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def db_putData(db,sql,data):
    """
    A generic function for creating or updating data within any table
    in a databse, based on the provided SQL statement and corresponding
    data.

    Args:
        db(string): The address of the database file to be written to.

        sql(string): An SQL statement to manipulate the data entry.

        data(tuple): A tuple corresponding to data to the PUT via the
        SQL statement.

    Returns:
        cur.lastrowid(int): On success, the row position in the table at which
        the data entry was created or edited.

        None: On failure to complete edit.

    Exceptions:
        e(string): An sqlite3 error message upon failure to create the user
    """

    try:
        conn = db_connect(db)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.lastrowid
    except Error as e:
        print(e)
        return None

def db_putDataMany(db,sql,data):
    """
    Like db_putData but uses the sql .execuate many method to allow for large 
    numbers of rows to be inserted in one transaction into the database.

    Args:
        db(string): The address of the database file to be written to.

        sql(string): An SQL statement to define the data input to be carried
        out for each row.

        dataMany(List (of tuples)): A list of tuples, each of which corresponds
        to a row of data to be PUT by the SQL statemet.

    """

    try:
        conn = db_connect(db)
        with conn:
            cur = conn.cursor()
            cur.executemany(sql, data)
            return cur.lastrowid
    except Error as e:
        print(e)
        return None


def db_getDataDict(db,sql,data):
    """
    A generic function for making a query to retreive data from a table within
    the database. Returns data as a List in which each element represents a
    database row, consisting of a dictionary with column headings as keys.

    Args:
        db(string): The address of the database file to be written to.

        sql(string): An SQL statement to query the database.

        data(tuple): A tuple corresponding to data to the retreived via the
        SQL statement.

    Returns:
        result(list(of dictionaries)): A list of dictionaries where each item is
        the data for a retreived row, and the dictionary keys are the requested
        table column headers. Returns None on failure to execute query.

    Exceptions:

        e(string): An sqlite3 error message upon failure to create the userExceptions:

    """
    result = []
    try:
        conn = db_connect(db)
        # Row_factory allows column headers to return with rows
        conn.row_factory = sqlite3.Row

        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            rows = cur.fetchall()

            # Convert to list of dictionaries
            for row in rows:
                result.append(dict(row))

            return result

    except Error as e:
        print(e)
        return None

""" Table creation functions and schema: """

def db_createTable(conn, createTableSQL):
    """
    Creates a table in a specifed database, using the provided SQL schema

    Args:
        conn(object): A database connection object

        createTableSQL(string): SQL defining the table schema

    Returns:
        Nothing - creates the table in the database

    Exceptions:
        e(string): An sqlite3 error message upon failure to connect to
                    create a table
    """
    try:
        c = conn.cursor()
        c.execute(createTableSQL)
    except Error as e:
        print(e)


# SQL Schema for the "users" table
createTableSQL_Users = """ CREATE TABLE IF NOT EXISTS users (
                                        user_id integer PRIMARY KEY AUTOINCREMENT,
                                        username text UNIQUE NOT NULL,
                                        password text NOT NULL,
                                        firstName text,
                                        secondName text,
                                        email text,
                                        locationPref text,
                                        localePref text,
                                        currencyPref text
                                        ); """

# SQL Schema for the "search_live_log" table
createTableSQL_search_live_log = """ CREATE TABLE IF NOT EXISTS search_live_log (
                                            search_id integer PRIMARY KEY AUTOINCREMENT,
                                            user_id integer,
                                            created timestamp,
                                            searchJson text,
                                            searchName text
                                            ); """

# SQL Schema for the "search_live_results" table
createTableSQL_search_live_results = """ CREATE TABLE IF NOT EXISTS search_live_results (
                                            results_id integer PRIMARY KEY AUTOINCREMENT,
                                            search_id integer NOT NULL,
                                            user_id integer,
                                            resultTimestamp timestamp,
                                            resultsJson text,
                                            searchName text
                                            ); """

# SQL Schema for the "search_live_data" table
createTableSQL_search_live_data = """ CREATE TABLE IF NOT EXISTS search_live_data (
                                            results_id integer,
                                            search_id integer,
                                            user_id integer,
                                            itineraryTimestamp timestamp,
                                            OutboundLegId text,
                                            Price text,
                                            QuoteAge text,
                                            InboundLegId text,
                                            linkURL text,
                                            OriginStationOB text,
                                            DestinationStationOB text,
                                            DepartureOB text,
                                            ArrivalOB text,
                                            DurationOB text,
                                            CarriersOB text,
                                            DirectionalityOB text,
                                            StopsOB text,
                                            OriginStationIB text,
                                            DestinationStationIB text,
                                            DepartureIB text,
                                            ArrivalIB text,
                                            DurationIB text,
                                            CarriersIB text,
                                            DirectionalityIB text,
                                            StopsIB text,
                                            stopsListOB text,
                                            carriersListOB text,
                                            stopsListIB text,
                                            carriersListIB text,
                                            OriginStationNameOB text,
                                            DestinationStationNameOB text,
                                            OriginStationNameIB text,
                                            DestinationStationNameIB text
                                            ); """


""" User account setting functions: """

def db_createUser(db, user):
    """
    Uses db_putData to create a new user entry in the database. Refer to db_putData
    for further information on returns and exceptions.

    Args:
        db(string): The address of the database file to be written to.

        user(tuple): A tuple containing the users information to be inserted
        as a new entry. The required elements and order are defined in the sql
        parameter below.
    """
    sql = ''' INSERT INTO users(username,password,firstName,secondName,email,
                                locationPref,localePref,currencyPref)
              VALUES(?,?,?,?,?,?,?,?) '''

    # Call PUT function
    return db_putData(db, sql, user)


def db_getUser(db, username):
    """
    Returns an dictionary object containing all user information for
    the provided username. Refer to db_putData for further information on
    exceptions.

    Args:
        db(string): The address of the database file to interogate

        username(string): The username to retrive the data for

    Returns:
        user(dict): A dictionary with all of the information for a single user.
        Keys are the column headings from the user table.  Returns None if user
        not present.
    """
    sql = "SELECT * FROM users WHERE username=?"

    # Call GET function
    result = db_getDataDict(db, sql, (username,))

    # Retrieve first / only value from list
    try:
        user = result[0]

    except:
        user = None

    return user

def db_getUserSearchHistory(db, user_id):
    """Returns a list of dictionaries comprising the user search history, obtained
    from the search_live_log table in the database.

    Args:
        db(string): The address of the database file to interogate

        user_id(integer): The unique identifier for the user.

    Returns:
        userSearchHistory(list(of dictionaries)): A list of dictionaries each
        comprising of data from the columns within the search_live_log table
        of the escapde database, for searches with matching user_id. Returns None
        on error.
    """
    sql = "SELECT * FROM search_live_log WHERE user_id=?"

    userSearchHistory = db_getDataDict(db, sql, (user_id,))

    return userSearchHistory

def db_getSearchQuery(db, search_id):
    """
    Returns a Python formatted search query from the database.

    Args:
        db(string): The address of the database file to interogate

        search_id(integer): The unique identifier for the search.

    Returns:
        queryList(list (of dictionaries): A list of dictionaries
        collectively comprising a live_search query.)
    """
    sql = "SELECT * FROM search_live_log WHERE search_id=?"

    queryDB = db_getDataDict(db, sql, (search_id,))
    queryJson = queryDB[0]["searchJson"]

    # Convert from json into Python
    queryList = json.loads(queryJson)

    return queryList

def db_getSearchResult(db, search_id):
    """
    Returns a Python formatted version of the stored skyscanner json
    response from a previous live search query

    Args:
        db(string): The address of the database file to interogate

        search_id(integer): The unique identifier for the search.

    Returns:
        responsHistoric (dictionary): A Python formatted json containing
        multiple lists and dictionaries, as recevied from the API endpoint.
    """
    sql = "SELECT resultsJson FROM search_live_results WHERE search_id=?"

    resultDB = db_getDataDict(db, sql, (search_id,))
    responseJson = resultDB[0]["resultsJson"]

    # Convert from json into Python
    responseHistoric = json.loads(responseJson)

    return responseHistoric


def db_updatePassword(db,newPassword,username):
    """
    Uses db_putData to ammend a users password hash. Refer to db_putData
    for further information on returns and exceptions.

    Args:
        db(string): The address of the database file to be written to

        newPassword(string): The new password hash.

        username(string): User's unique username.
    """

    sql = "UPDATE users SET password=? WHERE username=?"

    data = (newPassword, username)

    # Call PUT function
    return db_putData(db, sql, data)


""" User search history functions """

def db_logSLQuery(db, user_id, searchQuery):
    """
    Uses db_putData to log any search carried out using search_live as
    a .json with associated metadata.

    Refer to db_putData for further information on returns and exceptions.

    Args:
        db(string): The address of the database file to be written to.

        user_id(integer: User id for the search to be recorded against. May be
        "" if no user_id to be stored.

        searchQuery(list(of dictionaries)): A list of dictionaries, each
        containing keys required to construct an URL for the Live Flight
        Search API endpoint. Key value pairs are: "country", "currency",
        "locale","originplace","destinationplace", "outboundpartialdate","adults".

    Returns:
        search_id(integer): The last row id, which is the unique autoincrement
        value for search_id.

    """
    # Convert searchQuery into .json format for storage in the database
    searchJson = json.dumps(searchQuery)
    timestamp = datetime.now()

    data = (user_id, timestamp, searchJson)

    sql = ''' INSERT INTO search_live_log (user_id,created,searchJson)
                VALUES(?,?,?) '''

    # Call PUT function

    search_id = db_putData(db, sql, data)

    return search_id

def db_logSLResults(db, user_id, search_id, liveQuotesList):
    """
    Uses db_putData to log results retreived from search_live as a .json
    with associated metadata.  The  result are stored as a single .json object
    that is created from the list of .jsons returned from liveSearchRequestQuotes_T.

    Refer to db_putData for further information on returns and exceptions.

    Args:
        db(string): The address of the database file to be written to.

        user_id(integer): User id for the search to be recorded against. May be
        "" if no user_id to be stored.

        search_id(integer): The unique id of the search query for which the result
        is associated.

        liveQuotesList (List( of dictionaries): A list of dictionaries containing
        multiple API response .json.
        Refer to API documentation for structure.

    Returns:
        results_id(integer): The last row id, which is the unique autoincrement
        value for resutls_id.
    """
    # Convert liveQuotesList into .json format for storage in the database
    resultsJson = json.dumps(liveQuotesList)
    resultTimestamp = datetime.now()

    data = (search_id, user_id, resultTimestamp, resultsJson)

    sql = ''' INSERT INTO search_live_results(search_id,user_id,resultTimestamp,
                                            resultsJson)
                VALUES(?,?,?,?) '''

    # Call the PUT function
    results_id = db_putData(db, sql, data)

    return results_id

def db_logSLItineraries(db, user_id, search_id, results_id, resultsDict):
    """
    Uses db_putDataMany to log the formatted itinaries created by liveSearchFormatResult
    for analysis and presentation to the user, and the associated search
    metadata.
    Refer to db_putData for further information on returns and exceptions.

    Args:
        db(string): The address of the database file to be written to.

        user_id(integer): User id for the search to be recorded against. May be
        "" if no user_id to be stored.

        search_id(integer): The unique id of the search query for which the result
        is associated.

        results_id(integer): The unique id for the search result key from the
        search_live_data table.

        resultsDict (list(of dictionaries)): List of dictionaries containing the
        itinary data defined within liveSearchFormatResult in ss_api_functions.

    Constraints:
        This function works by defining a generic SQL insertion statement, and determines
        no number of variables to enter based on the number of key:value pair for the first 
        entry in resultsDict, which is different for one-way and return trips. As such if
        there are a mixture of return and single route trips in resultsDict, the SQL will
        not commit properly. This may be fixed as part of a future datastructure refactor,
        but does not currently affect core functionality of the program. 

    """

    # Create the SQL insertion to be used for each entry
    columns = "user_id,search_id,results_id,itineraryTimestamp," + ','.join(resultsDict[0].keys())
    # Placeholders for length of itinary, plus 3 id and 1 timestamp parameters
    itineraryLength = len(resultsDict[0])
    placeholders = ', '.join(['?'] * (itineraryLength + 4))
    sql = "INSERT INTO search_live_data(%s) VALUES (%s)" % (columns, placeholders)

    # Initialise values list
    values = []

    # For each itinerary dict in the list:
    for itinerary in resultsDict:
        # Create timestamp
        itineraryTimestamp = datetime.now()

        #Create a values tuple and append to list
        entry = (user_id, search_id, results_id,itineraryTimestamp) + tuple(itinerary.values())
        values.append(entry)

    # Call PUT MANY function
    db_putDataMany(db, sql, values)


"""Specific database operators and wrappers"""

def db_intialise(db):
    """
    Wrapper for use in app.py that creates (if none present) the database or
    updates the structure and associated schema if required.

    Args:
        None

    Returns:
        Creates or updates the application database.db file in the app.py directory

    Exceptions:
        TBD
    """

    # Connect to database
    conn = db_connect(db)

    if conn is not None:
        # create tables using schema defined above
        db_createTable(conn, createTableSQL_Users)
        db_createTable(conn, createTableSQL_search_live_log)
        db_createTable(conn, createTableSQL_search_live_results)
        db_createTable(conn, createTableSQL_search_live_data)

    else:
        print("Error! cannot create the database connection.")

    # Disconnect from database
    if conn:
        conn.close()


def main():
    """ Test Area"""
    # Create the database if it doesn't exist
    db = r"escapade.db"
    db_intialise(db)

    user_id = 2
    # trial search of the escapade database
    print(db_getUserSearchHistory(db, user_id))

    # Space reserved for testing


if __name__ == '__main__':
    main()
