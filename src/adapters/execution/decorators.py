from collections.abc import Callable

from core.models.definitions import DQTest
from core.models.enums import DQExecutionMode, DQTestScope, DQExecutionEngine


def dqtest(
    fn: Callable | None = None,
    name: str | None = None,
    *,
    scope: DQTestScope = DQTestScope.ROW_LEVEL,
    execution_mode: DQExecutionMode = DQExecutionMode.PYTHON,
    engine: DQExecutionEngine = DQExecutionEngine.SPARK,
):
    def wrapper(f: Callable):
        return DQTest(
            scope=scope,
            name=name if name else f.__name__,
            engine=engine,
            execution_mode=execution_mode,
            fn=f,
        )

    if callable(fn):
        return wrapper(fn)
    return wrapper


def dqtest_sql(
    fn: Callable | None = None,
    name: str | None = None,
    *,
    scope: DQTestScope = DQTestScope.ROW_LEVEL,
    engine: DQExecutionEngine = DQExecutionEngine.SPARK,
):
    return dqtest(
        fn=fn,
        name=name,
        scope=scope,
        execution_mode=DQExecutionMode.SQL,
        engine=engine,
    )


def dqtest_python(
    fn: Callable | None = None,
    name: str | None = None,
    *,
    scope: DQTestScope = DQTestScope.ROW_LEVEL,
    engine: DQExecutionEngine = DQExecutionEngine.SPARK,
):
    return dqtest(
        fn=fn,
        name=name,
        scope=scope,
        execution_mode=DQExecutionMode.PYTHON,
        engine=engine,
    )
