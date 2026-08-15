from enum import Enum


class DQTestScope(str, Enum):
    ROW_LEVEL = "ROW_LEVEL"
    COLUMN_LEVEL = "COLUMN_LEVEL"
