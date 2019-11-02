import sqlite3
from sqlite3 import Error


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


""" User account setting functions: """

def db_createUser(db, user):
    """
    Create a new user in the users table of the specifed database, using the
    information provided within the users object

    Args:
        db(string): The address of the database file to be written to

        user(tuple): A tuple containing the users information to be inserted
        as a new entry. The required elements and order are defined in the sql
        parameter below.

    Returns:
        cur.lastrowid(int): On success, the row position in the table at which
        the user was created.

        None: On failure to create user.

    Exceptions:
        e(string): An sqlite3 error message upon failure to create the user

    """

    sql = ''' INSERT INTO users(username,password,firstName,secondName,email,
                                locationPref,localePref,currencyPref)
              VALUES(?,?,?,?,?,?,?,?) '''
    try:
        conn = db_connect(db)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, user)
            return cur.lastrowid
    except Error as e:
        print(e)
        return None

def db_getUser(db, username):
    """
    Returns an object containing user details for the provided username, from
    the specified database.

    Args:
        db(string): The address of the database file to interogate

        username(string): The username to retrive the data for

    Returns:
        user(dict): A dictionary with all of the information for a single user.
        Keys are the column headings from the user table.  Returns None if user
        not present.

    Exceptions:
        N/A

    """
    sql = "SELECT * FROM users WHERE username=?"

    user = None
    try:
        conn = db_connect(db)
        # Row_factory allow column headers to return with rows
        conn.row_factory = sqlite3.Row

        with conn:
            cur = conn.cursor()
            cur.execute(sql, (username,))
            rows = cur.fetchall()

            # Convert to dictionary
            user = dict(rows[0])

    except:
        pass

    return user

def db_updatePassword(db,newPassword,username):
    """

    """
    sql = "UPDATE users SET password=? WHERE username=?"

    try:
        conn = db_connect(db)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, (newPassword, username))
            return cur.lastrowid
    except Error as e:
        print(e)
        return None



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
    db_createUser(db,user_2)

    result = db_getUser(db,"lcr")
    print(result["username"])
    print(result["user_id"])



if __name__ == '__main__':
    main()
