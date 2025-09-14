# builtin
from typing import Literal, Optional
# 3rd party
import pydantic
# local
from nimble.query import Query
from nimble.user_descriptor import UserDescriptor
from nimble.select import Select

class UserSelect(Select):
    descriptors: list[UserDescriptor] = []