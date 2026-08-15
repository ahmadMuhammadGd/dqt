from typing import List, Set
from dqt.abc.artifact_store import ArtifactStorePersist
from dqt.abc.execution_engine import ExecutionEngine
from dqt.types import Bind


class DQExplainer:
    def __init__(
        self,
        artifact_store: ArtifactStorePersist,
        execution_engine: ExecutionEngine,
    ):
        self.artifact_store = artifact_store
        self.execution_engine = execution_engine

    def explain(self, df, run_id_col_name: str | None = None):
        run_id_column = run_id_col_name or self.execution_engine.run_uuid_column_name

        run_ids: Set[str] = self.execution_engine.get_run_ids(df, run_id_column)
        run_id_test_bind_map: dict[str, List[Bind]] = self.artifact_store.get_binding(
            run_ids
        )
        return self.execution_engine.explain(run_id_test_bind_map)
