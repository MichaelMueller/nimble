# builtin
from typing import Literal, Optional
# 3rd party
import pydantic
from sqlalchemy import ColumnElement, Table, Column
# local

class FieldCondition(pydantic.BaseModel):
    type:str

    def to_bool_expression(self, column: Column) -> ColumnElement[bool]:
        raise NotImplementedError()