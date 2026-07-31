from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from core.models.enums import DQTestStatus


class DQTestResult(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    uuid: str = Field(default_factory=uuid4)

    bind_uuid: str
    status: DQTestStatus

    failed_rows: int = Field(default=0, ge=0)
    total_rows: int = Field(default=0, ge=0)

    @computed_field
    @property
    def is_passed(self) -> bool:
        return self.status == DQTestStatus.PASS

    @computed_field
    @property
    def failed_pct(self) -> float:
        if self.total_rows == 0:
            return 0.0
        return self.failed_rows * 100 / self.total_rows

    @computed_field
    @property
    def success_pct(self) -> float:
        return 100 - self.failed_pct

    @computed_field
    @property
    def success_rows(self) -> float:
        return self.total_rows - self.failed_rows

    @field_validator("uuid", mode="before")
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v
