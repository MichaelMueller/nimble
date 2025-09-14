# builtin
from typing import Optional, Any, Set, Type, TYPE_CHECKING
# 3rd party
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection
# local
if TYPE_CHECKING:
    from nimble.api import Api
from nimble.module import Module, Query

class UserModule(Module):

    def __init__(self, api: "Api"):
        super().__init__(api)
        self._initialized: bool = False
    
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