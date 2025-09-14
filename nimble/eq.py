# builtin
from typing import Literal, Optional, Any
# 3rd party
import pydantic
from sqlalchemy import ColumnElement, Table, Column
# local
from nimble.field_condition import FieldCondition

class Eq(FieldCondition):
    type:Literal["eq"] = "eq"
    value: str | int | float | bool | None

    def to_bool_expression(self, column: Column) -> ColumnElement[bool]:
        return column == self.value

    