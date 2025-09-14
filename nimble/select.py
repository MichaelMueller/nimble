# builtin
from typing import Literal, Optional
# 3rd party
import pydantic
from sqlalchemy import ColumnElement, Table, Column
from sqlalchemy import or_
# local
from nimble.descriptor import Descriptor

class Select(pydantic.BaseModel):
    descriptors: list[Descriptor] = []
    limit: Optional[int] = None
    offset: Optional[int] = None
    
    def to_bool_expression(self, table: Table) -> ColumnElement[bool] | None:        
        expressions = []
        for table_condition in self.descriptors:
            expr = table_condition.to_bool_expression(table)
            expressions.append(expr)
        return or_(*expressions) if expressions else None