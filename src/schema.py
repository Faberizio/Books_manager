from typing import TypedDict, Optional, Tuple
from datetime import date
from enum import Enum


class StatusEnum(Enum):
    reading = "reading"
    pending = "pending"
    complete = "complete"


class CreateDataType(TypedDict):
    username: str
    book_title: str
    book_desc: Optional[str]
    status: StatusEnum
    pct_read: int
    start_read_date: Optional[date]
    end_read_date: Optional[date]


FetchByIdDataType = Tuple[
                        str,
                        StatusEnum,
                        Optional[str],
                        int,
                        Optional[date],
                        Optional[date]]
