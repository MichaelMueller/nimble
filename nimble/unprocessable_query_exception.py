# builtin
from typing import Literal, Optional
# 3rd party
# local

class UnprocessableQueryException(Exception):
    
    def __init__(self, message: str):
        super().__init__(message)