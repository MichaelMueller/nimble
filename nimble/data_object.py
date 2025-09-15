# builtin
from pyexpat import model
from typing import Literal, Optional, Tuple, Type
# 3rd party
import pydantic
from pydantic.fields import PydanticUndefined

import sqlalchemy
from sqlalchemy import Table as SqlalchemyTable, Column, Integer, String, MetaData
from typing import get_origin, get_args, Union
# local

class DataObject(pydantic.BaseModel):        
    id:int
    
    @classmethod
    def to_sqlalchemy_table(cls, metadata:Optional[MetaData]=None, table_name:Optional[str]=None) -> Tuple[MetaData, SqlalchemyTable]:
        metadata = metadata or MetaData()
        columns = []
        for name, field in cls.model_fields.items():
            # Map pydantic types to SQLAlchemy types, handle Optional and defaults
            py_type = field.annotation
            nullable = field.is_required() == False
            default = field.get_default()          
            
            # Handle Union and Literal types
            origin = get_origin(py_type)
            types:set | None = None
            if origin is Union:
                types = { t for t in get_args(py_type) }
                if type(None) in types:
                    types.remove(type(None))
                    nullable = True
            elif origin is Literal:
                # For Literal, use the type of the first argument
                types = { t for t in get_args(py_type) }
            if types is not None:
                if len(types) > 1:
                    raise TypeError(f"Multiple types not supported for field {name}: {py_type}")
                py_type = types.pop()
                        
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

            columns.append(Column(
                name,
                col_type,
                nullable=nullable,
                default=None if default is PydanticUndefined else default,
                primary_key=(name == "id"),
                autoincrement=(name == "id")
            ))
        return metadata, SqlalchemyTable(table_name or cls.__name__, metadata, *columns)
    
    @classmethod
    def create_insert_pydanctic_model(cls) -> Type[pydantic.BaseModel]:
        fields = {}
        for name, field in cls.model_fields.items():
            if name == "id":
                continue
            fields[name] = (field.annotation, field.get_default() if not field.is_required() else ...)
        return pydantic.create_model(f"{cls.__name__}Insert", **fields)
    
    @classmethod
    def create_update_model(cls) -> Type[pydantic.BaseModel]:
        fields = {}
        for name, field in cls.model_fields.items():
            if name == "id":
                continue
            fields[name] = (Union[field.annotation, None], None)
        return pydantic.create_model(f"{cls.__name__}Update", **fields)

    @staticmethod
    def create_source(model: Type[pydantic.BaseModel]) -> str:
        imports = ["from pydantic import BaseModel"]
        lines = [f"class {model.__name__}(BaseModel):"]
        for name, field in model.model_fields.items():
            current_line:str = f"    {name}: "
            origin = get_origin(field.annotation)
            
            types:set | None = None
            if origin is Union:
                imports.append("from typing import Union")
                current_line += "Union["
                types = { t.__name__ if t != type(None) else "None" for t in get_args(field.annotation) }
                current_line += ", ".join(types) + "]"
            elif origin is Literal:
                imports.append("from typing import Literal")
                current_line += "Literal["
                types = { t.__name__ for t in get_args(field.annotation) }
                current_line += ", ".join(types) + "]"
            elif field.annotation in [int, str, float, bool, bytes]:
                current_line += f"{field.annotation.__name__}"
            else:
                imports.append("from " + field.annotation.__module__ + " import " + field.annotation.__name__)
                current_line += f"{field.annotation.__name__}"
                
            current_line += " = " + str(field.get_default()) if not field.is_required() else ""
            lines.append(current_line)
        lines = imports + [""] + lines
        source = "\n".join(lines)
        return source

