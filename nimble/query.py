# builtin
from typing import Literal, Optional
# 3rd party
import pydantic
# local

class Query(pydantic.BaseModel):
    token: Optional[str] = None # an arbitrary token that can be used to identify the user