from src.util import ROOT_DIR  # root directory for environ
# Class to hint that a parameter the insert_data function should receive has a default value of None is set.
from src.schema import CreateDataType
# Optional ^ / Union[type1, type2] means either type1 or type2.
from typing import Optional, Union
# Module to establish a connection to db specified in .env file.
import environ
import psycopg as pg  # PostgreSQL adapter module.
from datetime import date  # self explanatory.


# create a connection
env = environ.Env()

# set .env path to be read
environ.Env.read_env(str(ROOT_DIR / '.env'))


class Database:
    """SINGLETON CLASS for database connection.

    Args:
        object: default class definition in python, may be omitted.

    Returns:
        attribute: returns the user_defined _conn attribute of the connection variable.
    """
    _instance = None  # SINGLETON CLASS

    def __new__(cls):  # SINGLETON CLASS
        if Database._instance is None:
            Database._instance = super().__new__(cls)
            Database._instance.__init__()

        # Returns just the connection, not the instance itself.
        return Database._instance._conn

    # upon initiation defines private connection(_conn) attribute using env variable's (.env file) contents.
    def __init__(self) -> None:

        self._conn = pg.connect(
            host=env.str("db_host"),
            port=env.str("db_port"),
            user=env.str("db_user"),
            password=env.str("db_password"),
            dbname=env.str("dbname")
        )


def insert_data(data: CreateDataType) -> Optional[int]:
    """Function to insert data into database.

    Args:
        data (TypedDict): receives a dictionary consisting of the information necessary to create a row in the database.

    Returns:
        id (int): Returns integer representing the id (primary key) of the row created.
    """
    # get the connection
    conn = Database()

    # define the query
    query = """
            INSERT INTO read.book(
                username,
                title,
                status,
                pct_read,
                description,
                start_read_date,
                end_read_date
            ) VALUES(%s, %s, %s, %s, %s, %s, %s) RETURNING id;
    """

    # create a cursor session
    with conn.cursor() as cursor:
        # use the cursor session to execute the query. The execute method necessitates a query parameter, as well as an iterable consisting of the data to insert)
        cursor.execute(query, tuple(data.values()))
        # assign inserted_id variable to the first index of the row acquired by the fetchone() method.
        inserted_id = cursor.fetchone()[0]
        # commit changes to the database.
        conn.commit()
        # return the id of the row created.
        return inserted_id


def update_data(book_id: int, column: str, data: Union[str, date, int]):
    """Function to update existing data in a specific row of the database.

    Args:
        book_id (int): integer representing the row to be updated.
        column (str): string representing the column to be updated.
        data (either str, date, or int): data to be inserted into the specified id/column pair.

    Returns:
        id (int or None): returns id representing the row updated, or None if the id/row doesn't exist.
    """

    # Get connection.
    conn = Database()

    # Define query.
    query = """
    UPDATE read.book
    SET """ + column + """=%s
    WHERE id=%s RETURNING id;
    """
    # Begin cursor session with context manager.
    with conn.cursor() as cursor:
        # Run the query with the specified data.
        cursor.execute(query, [data, book_id])
        # Acquire id for the row updated if it exists, None if it doesn't.
        updated_book_id: Optional[int] = cursor.fetchone()[0]
        # Commit changes.
        conn.commit()
        # Return id of updated row.
        return updated_book_id


def fetch_by_id(book_id: int):
    """Class to fetch a row's contents by id

    Args:
        id (int): Integer representing the row to be updated.

    Returns:
        book (list): returns a list consisting of the row's contents.
    """

    # Get connection to the database.
    conn = Database()

    # Define the query.
    query = """
            SELECT
                title,
                status,
                pct_read,
                description,
                start_read_date,
                end_read_date
            FROM read.book
            WHERE id=%s;
    """

    # Begin cursor session with context manager.
    with conn.cursor() as cursor:
        # Run the query with the specified id.
        cursor.execute(query, (book_id,))
        # Assign the list returned by the fetchone() method to the book variable.
        book = cursor.fetchone()
        return book
