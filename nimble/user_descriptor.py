# builtin
from typing import Literal, Optional
# 3rd party
import pydantic
from sqlalchemy import ColumnElement, Table
# local
from nimble.descriptor import Descriptor
from nimble.field_condition import FieldCondition

class UserDescriptor(Descriptor):
    id: Optional[FieldCondition] = None
    username: Optional[FieldCondition] = None
    email: Optional[FieldCondition] = None
    password: Optional[FieldCondition] = None