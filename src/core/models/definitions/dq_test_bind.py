from hashlib import sha1
from typing import List
from pydantic import BaseModel, ConfigDict, Field, computed_field
from core.models.definitions.dq_test import DQTest
from core.models.enums.dq_severity import DQSeverity


class DQTestBind(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        frozen=True,
    )

    definition: DQTest
    error_threshold_pct: float = Field(default=100, ge=0, le=100)
    columns: tuple[str]
    ordinal: int = Field(ge=0)
    severity: DQSeverity = DQSeverity.LOW
    test_kwargs: dict[str, any] = Field(default_factory=dict)

    @computed_field
    def uuid(self) -> str:
        def_uuid = self.definition.uuid
        parts = (
            str(def_uuid),
            str(self.error_threshold_pct),
            str(self.columns),
            str(self.ordinal),
            str(self.severity.value),
        )
        return sha1("|".join(parts).encode()).hexdigest()
