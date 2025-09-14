# builtin
from typing import Literal, Optional
# 3rd party
import pydantic
# local
from nimble.query import Query

class UserCreate(Query):
    type:Literal["user_create"] = "user_create"
    username: str
    email: str
    password: str