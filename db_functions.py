import sqlite3
from sqlite3 import Error


""" Generic database helpers"""

def db_connect(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

""" Table creation functions and schema """

def db_createTable(conn, createTableSQL):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(createTableSQL)
    except Error as e:
        print(e)

# Create the user table tables TODO - OR UPDATE:
createTableSQL_Users = """ CREATE TABLE IF NOT EXISTS users (
                                        user_id integer PRIMARY KEY AUTOINCREMENT,
                                        username text NOT NULL,
                                        password text NOT NULL,
                                        firstName text,
                                        secondName text,
                                        email text,
                                        locationPref text,
                                        localePref text,
                                        currencyPref text
                                        ); """


""" User account setting functions """

def db_createUser(conn, user):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """

    sql = ''' INSERT INTO users(username,password,firstName,secondName,email,
                                locationPref,localePref,currencyPref)
              VALUES(?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, user)
    return cur.lastrowid



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
    conn = db_connect(db)
    with conn:
        # create new users

        user_1 = ("stm","abc","Sean","McNamara","sean@mail","UK","UK","GBP")
        user_2 = ("lcr","123","Lee","Ramsay","lee@mail","","","")

        db_createUser(conn,user_1)
        db_createUser(conn,user_2)



if __name__ == '__main__':
    main()
