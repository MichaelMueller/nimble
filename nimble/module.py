# builtin
from typing import Optional, Any, Set, Type, TYPE_CHECKING, Tuple
# 3rd party
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncConnection
# local
if TYPE_CHECKING:
    from nimble.api import Api
from nimble.query import Query, QuerySet

class Module:    
        
    async def initialize(self, api:"Api", db:Optional[AsyncConnection]) -> None:
        pass
    
    async def shutdown(self, api:"Api", db:Optional[AsyncConnection]) -> None:
        pass
            
    def pre_processable_queries(self) -> QuerySet:
        return set()

    async def pre_process(self, api:"Api", query:Query, db:AsyncConnection) -> None:
        pass
    
    def processable_queries(self) -> QuerySet:
        raise NotImplementedError()
    
    async def process(self, api:"Api", query:Query, db:AsyncConnection) -> Any:
        raise NotImplementedError()

    def post_processable_queries(self) -> QuerySet:
        return set()

    async def post_process(self, api:"Api", query:Query, db:AsyncConnection, result:Any) -> None:
        pass