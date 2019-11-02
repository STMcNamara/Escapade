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
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
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
    except:
        return None

def db_getUser(db, username):
    """
    Returns an object containing user details for the provided username
    """
    sql = "SELECT * FROM users WHERE username=?"

    row = None
    try:
        conn = db_connect(db)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, (username,))

            row = cur.fetchall()[0]
    except:
        pass

    return row



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

    db_createUser(db,user_1)
    db_createUser(db,user_2)

    result = db_getUser(db,"stm")
    print(result)



if __name__ == '__main__':
    main()
