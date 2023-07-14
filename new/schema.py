from typing import TypedDict, Optional, Tuple
from datetime import date
from enum import Enum


class StatusEnum(Enum):
    """Collection of name value pairs for the status column in db. Stating 3 possible values.

    Args:
        Enum: Class inherits from enum.Enum library/class. 
    """
    PENDING = 'pending'
    READING = 'reading'
    COMPLETE = 'complete'


class CreateDataType(TypedDict):
    """Creates a specific data type to be used in conjunction with the database.

    Args:
        TypedDict : Inherits from TypedDict class.
    """
    username: str
    title: str
    status: StatusEnum
    pct_read: Optional[int]
    description: Optional[str]
    start_read_date: Optional[date]
    end_read_date: Optional[date]


# Variable to hint the expected value from the fetch_by_id function.
FetchByIdDataType = Tuple[str, StatusEnum,
                          int, str, Optional[date], Optional[date]]
