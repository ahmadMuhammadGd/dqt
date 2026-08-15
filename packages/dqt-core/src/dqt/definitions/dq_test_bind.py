from hashlib import sha1
from typing import Any, Dict
from pydantic import BaseModel, ConfigDict, Field, computed_field
from dqt.definitions.dq_test import DQTest
from dqt.enums.dq_severity import DQSeverity


class DQTestBind(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        frozen=True,
    )

    definition: DQTest
    threshold_pct: float = Field(default=0, ge=0, le=100)
    columns: tuple[str] | Dict[str, str]
    ordinal: int = Field(ge=0)
    severity: DQSeverity = DQSeverity.LOW
    test_kwargs: dict[str, Any] = Field(default_factory=dict)

    @computed_field
    def uuid(self) -> str:
        def_uuid = self.definition.uuid
        parts = (
            str(def_uuid),
            str(self.threshold_pct),
            str(self.columns),
            str(self.ordinal),
            str(self.severity.value),
        )
        return sha1("|".join(parts).encode()).hexdigest()
