from hashlib import sha1
from typing import Any, Iterable

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
)

from core.models.definitions.dq_test import DQTest
from core.models.enums import DQExecutionEngine
from core.models.definitions.dq_test_bind import DQTestBind


class DQSuite(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        extra="forbid",
    )

    name: str

    engine: DQExecutionEngine

    test_binds: list[DQTestBind] = Field(default_factory=list)

    def bind_test(
        self,
        definition: DQTest,
        columns: str | Iterable[str],
        threshold_pct: float = 100,
        test_kwargs: dict[str, Any] = dict(),
    ) -> "DQSuite":
        if isinstance(columns, str):
            columns = (columns,)
        else:
            columns = tuple(columns)

        self.test_binds.append(
            DQTestBind(
                definition=definition,
                columns=columns,
                threshold_pct=threshold_pct,
                ordinal=len(self.test_binds),
                test_kwargs=test_kwargs,
            )
        )

        return self

    @computed_field
    @property
    def uuid(self) -> str:
        bind_uuids = "".join([t.uuid for t in self.test_binds])

        suite_uuid = bind_uuids + self.name + self.engine.value

        return sha1(suite_uuid.encode()).hexdigest()
