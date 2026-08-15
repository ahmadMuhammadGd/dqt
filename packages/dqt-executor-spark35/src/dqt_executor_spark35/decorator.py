from collections.abc import Callable

from pyspark.sql import Column, DataFrame

from dqt.decorators import dqtest_python, dqtest_sql
from dqt.enums import DQTestScope

from dqt_executor_spark35.config import _EXECUTOR_NAME

PySparkRowLevelTestCallable = Callable[[DataFrame], Column]
PySparkTableLevelTestCallable = Callable[[DataFrame], Column]


def dqtest_row_level_spark(
    fn: PySparkRowLevelTestCallable | None = None, *, name: str | None = None
):
    return dqtest_python(
        fn=fn,
        name=name if name else fn.__name__,
        scope=DQTestScope.ROW_LEVEL,
        engine=_EXECUTOR_NAME,
    )


def dqtest_row_level_sparkSQL(
    fn: PySparkRowLevelTestCallable | None = None, *, name: str | None = None
):
    return dqtest_sql(
        fn=fn,
        name=name if name else fn.__name__,
        scope=DQTestScope.ROW_LEVEL,
        engine=_EXECUTOR_NAME,
    )


def dqtest_column_level_spark(
    fn: PySparkRowLevelTestCallable | None = None, *, name: str | None = None
):
    return dqtest_python(
        fn=fn,
        name=name if name else fn.__name__,
        scope=DQTestScope.COLUMN_LEVEL,
        engine=_EXECUTOR_NAME,
    )


def dqtest_column_level_sparkSQL(
    fn: PySparkRowLevelTestCallable | None = None, *, name: str | None = None
):
    return dqtest_sql(
        fn=fn,
        name=name if name else fn.__name__,
        scope=DQTestScope.COLUMN_LEVEL,
        engine=_EXECUTOR_NAME,
    )
