from pydantic import ConfigDict, Field

from core.models.analytical.analytical_model import AnalyticalModel
from core.models.analytical.dim_bind import DimTestBind
from core.models.analytical.dim_dataset import DimDataset
from core.models.analytical.dim_suite import DimSuite
from core.models.analytical.dim_test import DimTest
from core.models.analytical.fact_run import FactRun
from core.models.analytical.fact_test_result import FactTestResult
from core.models.execution import DQExecutionResult


class AnalyticalMart(AnalyticalModel):
    model_config = ConfigDict(extra="forbid")

    binds: list[DimTestBind] = Field(default_factory=list)
    datasets: list[DimDataset] = Field(default_factory=list)
    suites: list[DimSuite] = Field(default_factory=list)
    tests: list[DimTest] = Field(default_factory=list)
    runs: list[FactRun] = Field(default_factory=list)
    results: list[FactTestResult] = Field(default_factory=list)

    @classmethod
    def from_execution_result(cls, result: DQExecutionResult):
        return cls(
            suites=DimSuite.from_execution_result(result),
            tests=DimTest.from_execution_result(result),
            runs=FactRun.from_execution_result(result),
            results=FactTestResult.from_execution_result(result),
            binds=DimTestBind.from_execution_result(result),
            datasets=DimDataset.from_execution_result(result),
        )
