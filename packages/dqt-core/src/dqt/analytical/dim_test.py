from uuid import UUID

from dqt.analytical.analytical_model import AnalyticalModel
from dqt.runtime.dq_run import DQRun


class DimTest(AnalyticalModel):
    table_name = "dim_test"
    primary_key = ["test_uuid"]

    test_uuid: str
    suite_uuid: str

    name: str
    description: str | None

    scope: str
    engine: str
    execution_mode: str

    test_implementation: str

    @classmethod
    def from_run(
        cls,
        run: DQRun,
    ) -> list["DimTest"]:

        suite = run.suite

        return [
            cls(
                test_uuid=str(bind.definition.uuid),
                suite_uuid=suite.uuid,
                name=bind.definition.name,
                description=bind.definition.description,
                scope=bind.definition.scope.value,
                engine=bind.definition.engine,
                execution_mode=bind.definition.execution_mode.value,
                test_implementation=bind.definition.test_implementation,
            )
            for bind in suite.test_binds
        ]
