from enum import Enum


class DQExecutionEngine(str, Enum):
    SPARK = "SPARK"
    PANDAS = "PANDAS"
