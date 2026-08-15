from enum import Enum


class DQTestStatus(str, Enum):
    PASS = "PASS"
    FAILED = "FAILED"
