import datetime
from enum import Enum
from tabulate import tabulate
from collections import namedtuple
from src.schema import StatusEnum, CreateDataType, FetchByIdDataType
from src.database import insert_data, fetch_by_id, update_data, delete_data,truncate_table, Database

class MenuDisplay:
    """
    MENU
    ----------
    1. DATA QUERY
        1. How many books were read completely during a specific period of time
        2. How many books are pending
        3. Search books by title
        4. Visualize table
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
    4. Visualize table
    77. Back To Menu
    """
        )
    
    @staticmethod
    def dq_completed_period():
        print("Number of books read completely during the specified period")
        start_date = validate_date_input("Enter the start date (YYYY-MM-DD): ")
        end_date = validate_date_input("Enter the end date (YYYY-MM-DD): ")
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
        print("Number of pending books")
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
                
    @staticmethod
    def visualize_table():
        db = Database()
        conn = db
        cursor = conn.cursor()

        query = """
            SELECT title, status, book_desc, pct_read, start_read_date, end_read_date
            FROM read.book;
        """
        cursor.execute(query)
        books = cursor.fetchall()

        headers = ["Title", "Status", "Description", "% Read", "Start Date", "End Date"]
        table = tabulate(books, headers=headers, tablefmt="fancy_grid")
        print(table)

        cursor.close()
        conn.close()


class InputOption:
    @staticmethod
    def input_option_dm_insert() -> CreateDataType:
        username = input("Username: ")
        print("Please, provide the following details: ")
        book_title = input("Book title: ")
        book_desc = input("(Optional) Describe the book: ")
        pct_read = input("(Optional) What percentage read: ")
        if pct_read:
            pct_read = validate_percentage_read(pct_read)
            if pct_read is None:
                return None
        
        start_read_date = None
        while not start_read_date or start_read_date > datetime.datetime.now().date():
            start_read_date_str = input("(Optional) Start reading date (YYYY-MM-DD): ")
            start_read_date = validate_date_input(start_read_date_str)
            if start_read_date is None or start_read_date > datetime.datetime.now().date():
                print("Start reading date must be in the past or present")

        end_read_date = None
        while not end_read_date or end_read_date <= start_read_date or end_read_date > datetime.datetime.now().date():
            end_read_date_str = input("(Optional) End reading date (YYYY-MM-DD): ")
            end_read_date = validate_date_input(end_read_date_str)
            if end_read_date is None:
                print("Invalid date format. Please use YYYY-MM-DD.")
            elif end_read_date <= start_read_date:
                print("End reading date must be after or equal to the start reading date")
            elif end_read_date > datetime.datetime.now().date():
                print("End reading date must be in the past or present")

        start_read_date = start_read_date.strftime("%Y-%m-%d")
        end_read_date = end_read_date.strftime("%Y-%m-%d")

        return {
            "username": username,
            "book_title": book_title,
            "book_desc": book_desc if book_desc else None,
            "status": StatusEnum.pending if not pct_read else get_status_from_percentage(pct_read),
            "pct_read": pct_read if pct_read else 0,
            "start_read_date": start_read_date if start_read_date else None,
            "end_read_date": end_read_date if end_read_date else None,
        }

    @staticmethod
    def input_option_dm_update():
        while True:
            id_to_update = input("Input book id to update: ")
            if not id_to_update.isdigit():
                print("Invalid book id. Please enter a valid integer.")
                continue
            
            id_to_update = int(id_to_update)
            book = fetch_by_id(id_to_update)
            if book is None:
                print("Book with that id doesn't exist. Please try again.")
                continue
            
            print("Book info: ")
            InputOption.generate_table(book)
            print(
                """
                Fields to update?
                1. Book title
                2. Status
                3. Description
                4. Percentage read
                5. Start date
                6. End date   
                """
            )
            field_option = input("What field do you want to change? ")
            if not field_option.isdigit():
                print("Invalid field option. Please enter a valid integer.")
                continue
            
            field_option = int(field_option)
            UpdatedInfo = namedtuple("UpdatedInfo", "book_id column value")

            if field_option == 1:
                book_title = input("Enter the new title: ")
                updated_info = UpdatedInfo(book_id=id_to_update, column="title", value=book_title)
                return updated_info
            elif field_option == 2:
                book_status = input("Enter the new status: ")
                updated_info = UpdatedInfo(book_id=id_to_update, column="status", value=book_status)
                return updated_info
            elif field_option == 3:
                description = input("Enter the new description: ")
                updated_info = UpdatedInfo(book_id=id_to_update, column="book_desc", value=description)
                return updated_info
            elif field_option == 4:
                pct_read = input("Enter the new read percentage: ")
                pct_read = validate_percentage_read(pct_read)
                if pct_read is None:
                    return None
                updated_info = UpdatedInfo(book_id=id_to_update, column="pct_read", value=pct_read)
                return updated_info
            elif field_option == 5:
                start_read_date_str = input("Enter the new start reading date (YYYY-MM-DD): ")
                start_read_date = validate_date_input(start_read_date_str)
                if start_read_date is None or start_read_date > datetime.datetime.now().date():
                    print("Invalid start reading date. Please use the format YYYY-MM-DD and provide a past or present date.")
                    continue
                start_read_date = start_read_date.strftime("%Y-%m-%d")
                updated_info = UpdatedInfo(book_id=id_to_update, column="start_reading_date", value=start_read_date)
                return updated_info
            elif field_option == 6:
                end_read_date_str = input("Enter the new end reading date (YYYY-MM-DD): ")
                end_read_date = validate_date_input(end_read_date_str)
                if end_read_date is None or end_read_date <= start_read_date or end_read_date > datetime.datetime.now().date():
                    print("Invalid end reading date. Please use the format YYYY-MM-DD, provide a date after or equal to the start reading date, and a past or present date.")
                    continue
                end_read_date = end_read_date.strftime("%Y-%m-%d")
                updated_info = UpdatedInfo(book_id=id_to_update, column="end_reading_date", value=end_read_date)
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


def validate_date_input(date_str):
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None

def validate_percentage_read(pct_read_str):
    try:
        pct_read = int(pct_read_str)
        if 0 <= pct_read <= 100:
            return pct_read
        else:
            print("Invalid value. Please enter a number between 0 and 100.")
            return None
    except ValueError:
        print("Invalid value. Please enter a number.")
        return None

def get_status_from_percentage(pct_read):
    if pct_read == 0:
        return StatusEnum.pending
    elif pct_read == 100:
        return StatusEnum.complete
    else:
        return StatusEnum.reading


def main():
    while True:
        MenuDisplay.display_menu()
        option = input("Choose an option to continue: ")
        if option == "1":
            print("OPERATION FOR QUERY")
            while True:
                MenuDisplay.display_DQ_menu()
                option = input("Choose an option to continue: ")
                if option == "1":
                    MenuDisplay.dq_completed_period()
                elif option == "2":
                    MenuDisplay.dq_pending()
                elif option == "3":
                    MenuDisplay.dq_search_title()
                elif option == "4":
                    MenuDisplay.visualize_table()
                elif option == "77":
                    break 
                elif option == "99":
                    print("Exiting the program")
                    return
                else:
                    print("Option not recognized. Please try again")
        elif option == "2":
            # OPERATION FOR MANIPULATION
            while True:
                MenuDisplay.display_DM_menu()
                option = input("Choose an option to continue: ")
                # INSERT
                if option == "1":
                    data = InputOption.input_option_dm_insert()
                    if data is not None:
                        # insert data to the database
                        id = insert_data(data)
                # UPDATE
                elif option == "2":
                    updated_data = InputOption.input_option_dm_update()
                    if updated_data is not None:
                        updated_id = update_data(
                            updated_data.book_id, updated_data.column, updated_data.value
                        )
                        if updated_id is not None:
                            print(f"Record with id {updated_id} updated successfully")
                        else:
                            print("Update failed!")
                # DELETE
                elif option == "3":
                    book_id_str = input("Enter the book ID to delete: ")
                    if not book_id_str.isdigit():
                        print("Invalid book ID. Please enter a valid integer.")
                        continue
                    book_id = int(book_id_str)
                    deleted_id = delete_data(book_id)
                    if deleted_id is not None:
                        print(f"Record with ID {deleted_id} deleted successfully")
                    else:
                        print("Deletion failed!")
                # TRUNCATE
                elif option == "4":
                    truncate_table()
                    print("Book table truncated successfully")
                elif option == "77":
                    break
                elif option == "99":
                    print("Exiting the program")
                    return
                else:
                    print("Option not recognized. Please try again")
        elif option == "99":
            # EXIT THE PROGRAM
            print("Exiting the program")
            break
        else:
            print("Option not recognized. Please try again")


if __name__ == "__main__":
    main()
