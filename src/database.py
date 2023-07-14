from typing import Optional, Union
import psycopg as pg
import environ
from datetime import date

from src.util import ROOT_DIR
from src.schema import CreateDataType, FetchByIdDataType

# CREATE A CONNECTION

env = environ.Env()
# set .env from the root dir to be read
environ.Env.read_env(str(ROOT_DIR / ".env"))


# SINGLETON CLASS.
class Database(object):
    _instance = None

    def __new__(cls):
        if Database._instance is None:
            Database._instance = super().__new__(cls)
            Database._instance.__init__()

        return Database._instance._conn

    def __init__(self) -> None:
        # It is bad practice to expose sensitive information in your code.
        self._conn = pg.connect(
            host=env.str("db_host"),
            dbname=env.str("db_name"),
            user=env.str("db_user"),
            password=env.str("db_password"),
            port=env.int("db_port"),
        )


def update_data(
    book_id: int, column: str, data: Union[str, date, int]
) -> Optional[int]:
    conn = Database()
    query = (
        """
    UPDATE read.book
    SET """
        + column
        + """=%s
    WHERE id=%s RETURNING id;
    """
    )

    with conn.cursor() as cursor:
        cursor.execute(query, [data, book_id])
        updated_book_id = cursor.fetchone()[0]
        conn.commit()
        return updated_book_id


def fetch_by_id(book_id: int) -> Optional[FetchByIdDataType]:
    conn = Database()

    query = """
        SELECT 
            title,
            status,
            book_desc,
            pct_read,
            start_read_date,
            end_read_date
        FROM read.book
        WHERE id=%s;   
    """
    with conn.cursor() as cursor:
        cursor.execute(query, [book_id])
        book = cursor.fetchone()
        return book


def insert_data(data: CreateDataType) -> Optional[int]:
    # get the connection
    conn = Database()
    # define the query
    query = """
        INSERT INTO read.book(
            username,
            title,
            book_desc,
            status,
            pct_read,
            start_read_date,
            end_read_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
    """
    # create a cursor session
    with conn.cursor() as cursor:
        # use the cursor session to execute the query
        cursor.execute(query, tuple(data.values()))  # OrderedDict
        inserted_id = cursor.fetchone()[0]
        conn.commit()
        return inserted_id

def delete_data(book_id: int) -> Optional[int]:
    conn = Database()
    query = """
        DELETE FROM read.book
        WHERE id = %s
        RETURNING id;
    """

    with conn.cursor() as cursor:
        cursor.execute(query, [book_id])
        deleted_id = cursor.fetchone()[0] if cursor.rowcount > 0 else None
        conn.commit()
        return deleted_id

def truncate_table():
    conn = Database()
    query = "TRUNCATE read.book;"

    with conn.cursor() as cursor:
        cursor.execute(query)
        conn.commit()
