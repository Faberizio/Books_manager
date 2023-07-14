from typing import Optional
from datetime import date
from tabulate import tabulate
from collections import namedtuple
from src.schema import StatusEnum, CreateDataType, FetchByIdDataType
from src.database import insert_data, fetch_by_id, update_data, delete_data,truncate_table, Database
import datetime

class MenuDisplay:
    """
    MENU
    ----------
    1. DATA QUERY
        1. How many books were read completely during a specific period of time
        2. How many books are pending
        3. Search books by title
        77. Go back to Menu
    2. DATA MANIPULATION
        1. INSERT DATA
        2. UPDATE DATA
        3. DELETE DATA
        4. TRUNCATE
        77. Go back to Menu
    """

    @staticmethod
    def display_menu():
        print(
            """
    WELCOME TO MY READ APP
        
    MENU
    ---------
    1. DATA QUERY
    2. DATA MANIPULATION
    99. Quit
    """
        )

    @staticmethod
    def display_DM_menu():
        print(
            """
    MENU > DATA MANIPULATION
    -------
    1. INSERT DATA
    2. UPDATE DATA
    3. DELETE DATA
    4. TRUNCATE
    77. Back To Menu
    """
        )

    @staticmethod
    def display_DQ_menu():
        print(
            """
    MENU > DATA QUERY
    ---------
    1. How many books were read completely during a specific period of time?
    2. How many books do we have pending?
    3. Search books by title?
    77. Back To Menu
    """
        )
    
    @staticmethod
    def dq_completed_period():
        #print("Number of books read completely during the specified period")
        start_date = input("Enter the start date (YYYY-MM-DD): ")
        end_date = input("Enter the end date (YYYY-MM-DD): ")
        query = """
            SELECT COUNT(*) FROM read.book
            WHERE status = 'complete' AND start_read_date >= %s AND end_read_date <= %s;
        """
        # Execute the query and fetch the result
        db = Database()
        conn = db
        with conn.cursor() as cursor:
            cursor.execute(query, [start_date, end_date])
            count = cursor.fetchone()[0]
            print(f"Number of books read completely during the specified period: {count}")


    @staticmethod
    def dq_pending():
        #print("Number of pending books")
        query = """
            SELECT COUNT(*) FROM read.book
            WHERE status = 'pending';
        """
        # Execute the query and fetch the result
        db = Database()
        conn = db
        with conn.cursor() as cursor:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            print(f"Number of pending books: {count}")


    @staticmethod
    def dq_search_title():
        print("Search books by title")
        title = input("Enter the book title: ")
        query = """
            SELECT * FROM read.book
            WHERE title ILIKE %s;
        """
        # Execute the query and fetch the result
        db = Database()
        conn = db
        with conn.cursor() as cursor:
            cursor.execute(query, ['%' + title + '%'])
            books = cursor.fetchall()
            if books:
                print("Matching books:")
                for book in books:
                        print(book)
            else:
                print("No books found with the given title.")


class InputOption:
    @staticmethod
    def input_option_dm_insert() -> CreateDataType:
        username = input("Username: ")
        print("Please, provide the following details: ")
        book_title: str = input("Book title: ")
        book_desc: str = input("(Optional) Describe the book: ")
        pct_read: str = input("(Optional) What percentage read: ")
        if pct_read:
            pct_read: int = int(pct_read)
            if pct_read == 0:
                status = "pending"
            elif pct_read == 100:
                status = "completed"
            elif pct_read < 100 and pct_read > 0:
                status = "reading"
            else:
                print("invalid value, please insert a number between 0 and 100")
        
        start_read_date = None
        while not start_read_date or start_read_date > datetime.datetime.now().date():
            start_read_date_str = input("(Optional) Start reading date (YYYY-MM-DD): ")
            try:
                start_read_date = datetime.datetime.strptime(start_read_date_str, "%Y-%m-%d").date()
                if start_read_date > datetime.datetime.now().date():
                    raise ValueError("Start reading date must be in the past or present")
            except ValueError as e:
                print(e)

        end_read_date = None
        while not end_read_date or end_read_date <= start_read_date or end_read_date > datetime.datetime.now().date():
            end_read_date_str = input("(Optional) End reading date (YYYY-MM-DD): ")
            try:
                end_read_date = datetime.datetime.strptime(end_read_date_str, "%Y-%m-%d").date()
                if end_read_date < start_read_date or end_read_date > datetime.datetime.now().date():
                    raise ValueError("End reading date must be after or equal to the start reading date")
            except ValueError as e:
                print(e)

        start_read_date = start_read_date.strftime("%Y-%m-%d")
        end_read_date = end_read_date.strftime("%Y-%m-%d")

        return {
            "username": username,
            "book_title": book_title,
            "book_desc": book_desc if book_desc else None,
            "status": status if status else StatusEnum.pending,
            "pct_read": pct_read if pct_read else 0,
            "start_read_date": start_read_date if start_read_date else None,
            "end_read_date": end_read_date if end_read_date else None,
        }

    @staticmethod
    def input_option_dm_update():
        while True:
            id_to_update: int = int(input("Input book id to update: "))
            book: Optional[FetchByIdDataType] = fetch_by_id(id_to_update)
            if book is None:
                print("Book by that id doesn't exist. Please,  try again")
                continue
            else:
                # display the book info in a table
                print("Book info: ")
                InputOption.generate_table(book)
                print(
                    """
                    Fields to update?
                    1. book title
                    2. status
                    3. description
                    4. pct read
                    5. start date
                    6. end date   
                """
                )
                field_option = int(input("What field do you want to change? "))
                UpdatedInfo = namedtuple("UpdatedInfo", "book_id column value")

                # UPDATE title
                if field_option == 1:
                    book_title = input("Enter the new title: ")
                    updated_info = UpdatedInfo(
                        book_id=id_to_update, column="title", value=book_title
                    )
                    return updated_info
                elif field_option == 2:
                    book_status = input("Enter the new status: ")
                    updated_info = UpdatedInfo(
                        book_id=id_to_update, column="status", value=book_status
                    )
                    return updated_info
                
                elif field_option == 3:
                    description = input("Enter the new description: ")
                    updated_info = UpdatedInfo(
                        book_id=id_to_update,
                        column="book_desc",
                        value=description
                    )
                    return updated_info

                elif field_option == 4:
                    pct_read = input("Enter the new read percentage: ")
                    updated_info = UpdatedInfo(
                        book_id=id_to_update, column="pct_read", value=pct_read
                    )
                    return updated_info
                elif field_option == 5:
                    STRD = input("Enter the new title: ")
                    updated_info = UpdatedInfo(
                        book_id=id_to_update, column="start_reading_date", value=STRD
                    )
                    return updated_info
                elif field_option == 6:
                    ENRD = input("Enter the new title: ")
                    updated_info = UpdatedInfo(
                        book_id=id_to_update, column="end_reading_date", value=ENRD
                    )
                    return updated_info
                else:
                    print("Option not recognized")

    @staticmethod
    def generate_table(data):
        table = [
            ["title", "status", "desc", "pct", "SD", "ED"],
            data,
        ]
        print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))


def main():
    while True:
        MenuDisplay.display_menu()
        option: int = int(input("Choose an option to continue: "))
        if option == 1:
            print("OPERATION FOR QUERY")
            while True:
                MenuDisplay.display_DQ_menu()
                option: int = int(input("Choose an option to continue: "))
                if option == 1:
                    MenuDisplay.dq_completed_period()
                elif option == 2:
                    MenuDisplay.dq_pending()
                elif option == 3:
                    MenuDisplay.dq_search_title()
                elif option == 77:
                    break 
                elif option == 99:
                    print("Exiting the program")
                    return
                else:
                    print("Option not recognized. Please try again")
        elif option == 2:
            # OPERATION FOR MANIPULATION
            while True:
                MenuDisplay.display_DM_menu()
                option: int = int(input("Choose an option to continue: "))
                # INSERT
                if option == 1:
                    data: CreateDataType = InputOption.input_option_dm_insert()
                    # insert data to the database
                    id = insert_data(data)
                # UPDATE
                elif option == 2:
                    updated_data = InputOption.input_option_dm_update()
                    updated_id = update_data(
                        updated_data.book_id, updated_data.column, updated_data.value
                    )
                    if updated_id is not None:
                        print(f"Record with id {updated_id} updated successfully")
                    else:
                        print("Update failed!")

                elif option == 3:
                    book_id = int(input("Enter the book ID to delete: "))
                    deleted_id = delete_data(book_id)
                    if deleted_id is not None:
                        print(f"Record with ID {deleted_id} deleted successfully")
                    else:
                        print("Deletion failed!")
                elif option == 4:
                    truncate_table()
                    print("Book table truncated successfully")
                elif option == 77:
                    break
                #elif option == 99:
                    # TODO: EXIT
                    #pass

        elif option == 99:
            # EXIT THE PROGRAM
            print("EXIT THE PROGRAM")
            break
        else:
            print("Option not recognized. Please try again")


if __name__ == "__main__":
    main()
