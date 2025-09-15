# builtin
from typing import Literal, Optional
# 3rd party
import pydantic
import sqlalchemy
from sqlalchemy import Table as SqlalchemyTable, Column, Integer, String, MetaData
from typing import get_origin, get_args, Union
# local

class Table(pydantic.BaseModel):
    
    
    def to_sqlalchemy_table(self, metadata:MetaData) -> SqlalchemyTable:
        metadata = MetaData()
        columns = []
        for name, field in self.model_fields.items():
            # Map pydantic types to SQLAlchemy types, handle Optional and defaults
            py_type = field.annotation
            nullable = False
            default = pydantic.fields.Undefined

            # Handle Optional (Nullable)
            # Handle Optional (Nullable) using typing.get_args and get_origin
            origin = get_origin(py_type)
            if origin is Union:
                args = get_args(py_type)
                if type(None) in args:
                    nullable = True
                    # Remove NoneType from args to get the actual type
                    py_type = next(arg for arg in args if arg is not type(None))

            # Map types
            if py_type == int:
                col_type = Integer
            elif py_type == str:
                col_type = String
            elif py_type == float:
                col_type = sqlalchemy.Float
            elif py_type == bool:
                col_type = sqlalchemy.Boolean
            elif py_type == bytes:
                col_type = sqlalchemy.LargeBinary
            else:
                raise TypeError(f"Unsupported field type: {py_type} for field {name}")  

            # Handle default values
            if field.default is not pydantic.fields.Undefined:
                default = field.default

            columns.append(Column(
                name,
                col_type,
                nullable=nullable,
                default=default if default is not pydantic.fields.Undefined else None
            ))
            columns.append(Column(name, col_type))
        return SqlalchemyTable(self.__class__.__name__, metadata, *columns)