from dqt.definitions import DQTest
from dqt.enums import DQExecutionMode, DQTestScope
from dqt.definitions.dq_test_bind import DQTestBind


def filter_by_execution_mode(binds: list[DQTestBind], mode: DQExecutionMode):
    if not mode:
        return binds
    return [i for i in binds if i.definition.execution_mode == mode]


def filter_by_scope(binds: list[DQTestBind], scope: DQTestScope):
    if not scope:
        return binds
    return [i for i in binds if i.definition.scope == scope]
