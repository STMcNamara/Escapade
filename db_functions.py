import sqlite3
from sqlite3 import Error
import json
from datetime import datetime


""" Generic database helpers:"""

def db_connect(db_file):
    """
    Create a connection object to the database. If no database exists, will
    creat that database

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

def db_getDataDict(db,sql,data):
    """
    A generic function for making a query to retreive data from a table within
    the database.

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

# SQL Schema for the "search_live_history table"
createTableSQL_search_live_history = """ CREATE TABLE IF NOT EXISTS search_live_log (
                                            search_id integer PRIMARY KEY AUTOINCREMENT,
                                            user_id integer,
                                            created timestamp,
                                            searchJson text,
                                            searchName text
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
    Uses db_putData to create log any search carried out using search_live as
    a .json with associated metadata.

    Refer to db_putData for further information on returns and exceptions.

    Args:
        db(string): The address of the database file to be written to.

        user_id(integer: User id for the search to be recorded against.

        timestamp(TBD): TODO

        searchQuery(list(of dictionaries)): A list of dictionaries, each
        containing keys required to construct an URL for the Live Flight
        Search API endpoint. Key value pairs are: "country", "currency",
        "locale","originplace","destinationplace", "outboundpartialdate","adults".

    """
    # Convert searchQuery into .json format for storage in the database
    searchJson = json.dumps(searchQuery)
    timestamp = datetime.now()

    data = (user_id, timestamp, searchJson)

    sql = ''' INSERT INTO search_live_log (user_id,created,searchJson)
                VALUES(?,?,?) '''

    # Call PUT function
    return db_putData(db, sql, data)



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
        # create tables using schema defined above [TODO consider updating]
        db_createTable(conn, createTableSQL_Users)
        db_createTable(conn, createTableSQL_search_live_history)

    else:
        print("Error! cannot create the database connection.")

    # Disconnect from database
    if conn:
        conn.close()


def main():
    """ Test Area"""
    # Create the database if it doesn't exist
    db = r"test.db"
    db_intialise(db)

    # Connect to database
    user_1 = ("stm","abc","Sean","McNamara","sean@mail","UK","UK","GBP")
    user_2 = ("lcr","123","Lee","Ramsay","lee@mail","","","")

    x = db_createUser(db,user_1)
    # Test create user
    db_createUser(db,user_2)

    # Test log search
    user_id = 123
    searchQuery = [{"a":1, "b":2, "c":3}]
    db_logSLQuery(db, user_id, searchQuery)

    result = db_getUser(db,"lcr")
    print(result["username"])
    print(result["user_id"])



if __name__ == '__main__':
    main()
