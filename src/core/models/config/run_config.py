from pydantic import BaseModel
from enums.dq_run_options_representation import Representation


class DQRunOptions(BaseModel):
    representation: Representation = Representation.INLINE
