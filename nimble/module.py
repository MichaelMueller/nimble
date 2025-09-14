# builtin
from typing import Optional, Any, Set, Type, TYPE_CHECKING
# 3rd party
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection
# local
if TYPE_CHECKING:
    from nimble.api import Api
from nimble.query import Query

class Module:    
    
    def __init__(self, api: "Api"):
        self._api = api
        self._initialized: bool = False
    
    def api(self) -> "Api":
        return self._api
    
    async def initialize(self, db:AsyncConnection) -> None:
        if not self._initialized:
            await self._initialize(db)
        self._initialized = True    
    
    async def shutdown(self, db:AsyncConnection) -> None:
        if self._initialized:
            try:
                await self._shutdown(db)
            finally:
                self._initialized = False
    
    async def _initialize(self, db:AsyncConnection) -> None:
        pass

    async def _shutdown(self, db:AsyncConnection) -> None:
        pass    
        
    def get_executable_queries(self) -> Set[Type["Query"]]:
        raise NotImplementedError()
    
    async def execute(self, query:Query, db:AsyncSession) -> Any:
        raise NotImplementedError()
            
    def pre_execute_for(self) -> Set[Type["Query"]]:
        return set()

    async def pre_execute(self, query:Query, db:AsyncSession) -> None:
        pass

    def post_execute_for(self) -> Set[Type["Query"]]:
        return set()

    async def post_execute(self, query:Query, db:AsyncSession, result:Any) -> None:
        pass