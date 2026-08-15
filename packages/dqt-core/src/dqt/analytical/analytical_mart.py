from pydantic import ConfigDict, Field

from dqt.analytical.analytical_model import AnalyticalModel
from dqt.analytical.dim_bind import DimTestBind
from dqt.analytical.dim_dataset import DimDataset
from dqt.analytical.dim_suite import DimSuite
from dqt.analytical.dim_test import DimTest
from dqt.analytical.fact_run import FactRun
from dqt.analytical.fact_test_result import FactTestResult
from dqt.runtime.dq_run import DQRun


class AnalyticalMart(AnalyticalModel):
    model_config = ConfigDict(extra="forbid")

    binds: list[DimTestBind] = Field(default_factory=list)
    datasets: list[DimDataset] = Field(default_factory=list)
    suites: list[DimSuite] = Field(default_factory=list)
    tests: list[DimTest] = Field(default_factory=list)
    runs: list[FactRun] = Field(default_factory=list)
    results: list[FactTestResult] = Field(default_factory=list)

    @classmethod
    def from_run(cls, run: DQRun):
        return cls(
            suites=DimSuite.from_run(run),
            tests=DimTest.from_run(run),
            runs=FactRun.from_run(run),
            results=FactTestResult.from_run(run),
            binds=DimTestBind.from_run(run),
            datasets=DimDataset.from_run(run),
        )
