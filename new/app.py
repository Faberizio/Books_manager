import sys  # for exiting program.
from typing import Optional  # for type hinting.
from datetime import date  # for date values.
from collections import namedtuple  # to define 'mutable' tuples.
from tabulate import tabulate  # to return some objects as a stylized table.
from src.schema import StatusEnum, CreateDataType, FetchByIdDataType
from src.database import insert_data, fetch_by_id, update_data


class MenuDisplay:
    """
    MENU
    ----------
    1. DATA QUERY
       1. How many books were read completely during a specific period of time
       2. How many books are pending
       3. Search books by title
       77. Go back to Menu
       99. Exit
    2. DATA MANIPULATION
       1. INSERT DATA
       2. UPDATE DATA
       3. DELETE DATA
       4. TRUNCATE
       77. Go back to Menu
       99. Exit

    99. Exit
    """

    # Static method since this class will not be instantiated.
    @staticmethod
    def display_menu():
        """Displays a CLI menu with options for the user."""

        # Print menu
        print(
            """
            WELCOME TO MY READ APP
            
            Menu
            ----
            1.DATA QUERY
            2. DATA MANIPULATION
            99. QUIT
            """
        )

    @staticmethod
    def display_DM_menu():
        """Displays a DATA MANIPULATION menu with options for the user."""
        print(
            """
        MENU > DATA MANIPULATION
        ----
        1. INSERT DATA
        2. UPDATE DATA
        3. DELETE DATA
        4. TRUNCATE
        77. BACK TO MENU
        99. QUIT
        """
        )

    @staticmethod
    def display_DQ_menu():
        """Displays a DATA QUERY menu with options for the user."""
        print(
            """
            MENU > DATA QUERY
            -----
            1. how many books were read completely during a specific period of time?
            2. How many books do we have pending?
            3. Search books by title
            77. Back to menu
            99. Quit
            """
        )


class InputOption():
    """Class representing all methods for DATA MANIPULATION
    """

    @staticmethod
    def input_option_dm_insert() -> CreateDataType:
        """ This method is used in the event of the user deciding for the input option from the DM menu.

    Returns:
        dict: returns a dictionary consisting of the information to be used for the creation of a row in the database.
    """
        # TODO: Add login feature and extract the username from there.
        username = 'Jose'
        print("Please, provide the following details: ")

        book_title: str = input('Book title: ')

        book_description: str = input('(Optional) Book description: ')

        status: StatusEnum = input(
            '(Optional) What is your current read status (pending, reading, complete): ')

        pct_read: str = input("(Optional) What percentage have you read: ")
        if pct_read:
            pct_read = int(pct_read)

        start_read_date: str = input(
            "(Optional) Start reading date (YYY-MM-DD): ")
        if start_read_date:
            start_read_date = date.fromisoformat(start_read_date)

        end_read_date: str = input("(Optional) End reading date (YYY-MM-DD): ")
        if end_read_date:
            end_read_date = date.fromisoformat(end_read_date)

        # NOTICE the returned dictionary has logic implemented to assign None, 0 or 'pending' to values that are NULLABLE in our database.
        return {
            'username': username,
            'title': book_title,
            'status': status if status else StatusEnum.PENDING,
            'pct_read': pct_read if pct_read else 0,
            'description': book_description if book_description else None,
            'start_read_date': start_read_date if start_read_date else None,
            'end_read_date': end_read_date if end_read_date else None
        }

    @staticmethod
    def input_option_dm_update() -> None:
        """ This method is used in the event of the user deciding for the update option from the DM menu.

    Returns:
        dict: returns the a tuple consisting of the id for the row to be updated, the column to be updated, and the value to be inserted.
        """
        # Create an open loop to mantain this state unless specified by the user.
        while True:
            # input assigned to a variable to acquire row id from the user
            id_to_update: int = int(input("Enter book id to update: "))
            # book variable hinted to be optionally of the custom Tuple type FetchIdByDataType. Assigned to it is the fetch_by_id function with the id as parameter.
            book: Optional[FetchByIdDataType] = fetch_by_id(id_to_update)

            # if the previous variable statement raises an exception, print a message and restart at the beginning of the loop.
            if book is None:
                print("Book id does not exist")
                continue
            else:  # otherwise print the book information in a stylized table with the generate_table method.
                print('Book info: ')
                InputOption.generate_table(book)
                # Followed by a menu stating the columns that may be updated.
                print("""
    Fields to update
    1. title
    2. status
    3. pct_read
    4. description
    5. start_read_date
    6. end_read_date
    77. Back to menu
    99. Exit
    """)
                # define a field_option variable to store the user input.
                field_option = int(
                    input("What field would you like to change? (1-6): "))

                # define an UpdatedInfo variable to a namedtuple with the specific information needed for updating in the database.
                UpdatedInfo = namedtuple('UpdatedInfo', 'book_id column value')

                # if user input is 1 (change book title)
                if field_option == 1:
                    # Input new title
                    book_title = input("Enter the new title: ")
                    # define updated_info variable cosisting of our previously stated nametuple with its values updated to those necessary for updating in the db.
                    updated_info = UpdatedInfo(
                        book_id=id_to_update, column="title", value=book_title)
                    # return last variable for visualization of the user.
                    return updated_info

                elif field_option == 2:
                    read_status = input(
                        "Enter the new status: (pending, reading, complete)")
                    updated_info = UpdatedInfo(
                        book_id=id_to_update, column="status", value=read_status)
                    return updated_info

                elif field_option == 3:
                    pct_read = input(
                        "Please enter the current read percentage (0-100): ")
                    updated_info = UpdatedInfo(
                        book_id=id_to_update, column="pct_read", value=pct_read)
                    return updated_info

                elif field_option == 4:
                    book_desc = input("Please enter a new book description: ")
                    updated_info = UpdatedInfo(
                        book_id=id_to_update, column="description", value=book_desc)
                    return updated_info

                elif field_option == 5:
                    sd = input("Please enter a start date: ")
                    updated_info = UpdatedInfo(
                        book_id=id_to_update, column="start_read_date", value=sd)
                    return updated_info

                elif field_option == 6:
                    ed = input("Please enter a end date: ")
                    updated_info = UpdatedInfo(
                        book_id=id_to_update, column="end_read_date", value=ed)
                    return updated_info

                # TODO: NEEDS FIXING.
                elif field_option == 77:
                    break
                # Exits the program entirely.
                elif field_option == 99:
                    sys.exit()

                # failsafe
                else:
                    print("Command not recognized, please try again.")

    @staticmethod
    def generate_table(data: tuple):
        """This function generates a table using the tabulate function from the tabulate library.

        Args:
            data (tuple): Tuple consisting of data to be used in the table.

        Prints:
            table (tabulate): Tuple converted into a "fancy_grid" style table, includes header.
        """

        # table list consisting of a nested list representing the columns in the table / header + data tuple.
        table = [
            [
                "title",
                "status",
                "pct_read",
                "description",
                "SD",
                "ED"
            ],
            data,
        ]
        print(tabulate(table,
                       headers="firstrow",
                       tablefmt="fancy_grid"))


def main():
    """EVENT LOOP, defines program execution logic.
    """

    # Open loop to maintain state unless user explicitly specifies otherwise.
    while True:
        # Display the menu
        MenuDisplay.display_menu()
        # Prompt user option and assign it to option variable
        option = int(input("Choose an option to continue: "))
        # If option is 1, print DATA QUERY MENU and continue its logic.
        if option == 1:
            print('OPERATION FOR QUERY')

        # If option is 2, print DATA MANUPULATION MENU and continue its logic.
        elif option == 2:
            # Open loop to maintain state.
            while True:
                # Display DM menu.
                MenuDisplay.display_DM_menu()
                # Prompt for user input and assign to option variable
                option = int(input("Choose an option to continue: "))

                # if user option is 1, collect data and assign it to data variable.
                if option == 1:
                    data: CreateDataType = InputOption.input_option_dm_insert()
                    # insert into database and assign returned id to id variable.
                    id = insert_data(data)

                # if user option is 2, collect data and assign it to updated_data variable.
                elif option == 2:
                    updated_data = InputOption.input_option_dm_update()
                    # returned id from update_data function assigned to updated_id variable.
                    updated_id = update_data(updated_data.book_id,
                                             updated_data.column, updated_data.value)

                    # if previous statement didn't raise exception, print success message.
                    if updated_id is not None:
                        print(
                            f"Record with id: {updated_id} updated successfully.")
                    # Otherwise print failure message.
                    else:
                        print("Update failed.")

                elif option == 3:
                    # TODO: DELETE DATA
                    pass
                elif option == 4:
                    # TODO: TRUNCATE
                    pass
                elif option == 77:
                    break
                elif option == 99:
                    sys.exit()

        elif option == 99:
            print('EXIT THE PROGRAM')
            break
        else:
            print("Option not recognized, please try again.")


if __name__ == "__main__":
    main()
