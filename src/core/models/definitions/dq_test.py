from collections.abc import Callable
from hashlib import sha1
from inspect import getdoc, getsource
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, computed_field

from core.models.enums import (
    DQExecutionMode,
    DQTestScope,
    DQExecutionEngine,
)


class DQTest(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        frozen=True,
        extra="forbid",
    )

    # test definition
    name: str
    fn: Callable[..., Any] = Field(exclude=True)
    scope: DQTestScope = DQTestScope.ROW_LEVEL
    engine: DQExecutionEngine = DQExecutionEngine.SPARK
    execution_mode: DQExecutionMode = DQExecutionMode.PYTHON

    @computed_field
    def test_implementation(self) -> str:
        return getsource(self.fn)

    @computed_field
    def description(self) -> str | None:
        return getdoc(self.fn)

    @computed_field
    def uuid(self) -> str:
        parts = (
            self.name,
            "" if not self.description else self.description,
            self.engine.value,
            self.scope.value,
            self.execution_mode.value,
            self.test_implementation,
        )

        return sha1("|".join(parts).encode()).hexdigest()
