# builtin
from typing import Literal, Optional
# 3rd party
import pydantic
from sqlalchemy import ColumnElement, Table, Column
from sqlalchemy import and_
# local
from nimble.field_condition import FieldCondition

class Descriptor(pydantic.BaseModel):

    def to_bool_expression(self, table: Table) -> ColumnElement[bool] | None:
        expressions = []
        for field_name in self.model_dump(exclude_unset=True).keys():
            column_condition:FieldCondition = getattr(self, field_name)
            
            column = table.c.get(field_name)
            expr = column_condition.to_bool_expression(column)
            expressions.append(expr)
        return and_(*expressions) if expressions else None
