# builtin
from typing import Literal, Optional, Set, Type
# 3rd party
import pydantic
# local

class Query(pydantic.BaseModel):
    pass    

QuerySet = Set[ Type[Query] ]