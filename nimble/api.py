# builtin
from typing import Optional, Union, AsyncGenerator, Callable, Type, Any, Literal, TYPE_CHECKING
import logging
# 3rd party
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncConnection, AsyncEngine, async_sessionmaker
# local
from nimble.module import Module
from nimble.query import Query
from nimble.api_config import ApiConfig

class Api:
    def __init__(self, config:Optional[ApiConfig]=None):       
        self._api_config = config or ApiConfig()
        # state 
        self._modules:dict[Type[Query], Module] = {}
        
        # db
        self._engine: Optional[AsyncEngine] = None
        self._async_sessionmaker: Optional[async_sessionmaker] = None

    async def register_module(self, module_type:Type[Module]) -> Module:        
        module = module_type(self)
        
        executable_queries = module.get_executable_queries()
        for query_type in executable_queries:
            if query_type in self._modules:
                raise ValueError(f"Query type {query_type.__name__} is already registered by module {self._modules[query_type].__class__.__name__}")
        
        engine = self._get_engine()
        async with engine.connect() as conn:
            await module.initialize(conn)
            
        for query_type in executable_queries:
            self._modules[query_type] = module
                        
        return module

    async def unregister_module(self, module:Module) -> None:
        for query_type, mod in list(self._modules.items()):
            if mod == module:
                del self._modules[query_type]   
        
        engine = self._get_engine()
        async with engine.connect() as conn:
            await module.shutdown(conn)

    async def execute(self, query:Query) -> Any:               
        if type(query) not in self._modules:
            raise ValueError(f"No module registered to handle query type {type(query).__name__}")
        
        # determine hooks
        unique_modules = set(self._modules.values())
        pre_execute_hooks = {mod for mod in unique_modules if type(query) in mod.pre_execute_for()}
        post_execute_hooks = {mod for mod in unique_modules if type(query) in mod.post_execute_for()}

        session_maker = self._get_async_session_maker()
        async with session_maker() as db:

            for hook in pre_execute_hooks:
                await hook.pre_execute(query, db)
            
            module = self._modules[type(query)]
            result = await module.execute(query, db)

            for hook in post_execute_hooks:
               await hook.post_execute(query, db, result)
                
            return result

    async def shutdown(self) -> None:        
        for module in list(self._modules.values()):
            try:
                await self.unregister_module(module)
            except Exception as e:
                logging.error(f"Error shutting down module {module.__class__.__name__}: {e}")

        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
        self._async_sessionmaker = None
    
    def _get_async_session_maker(self) -> async_sessionmaker:
        if self._async_sessionmaker is None:
            self._async_sessionmaker = async_sessionmaker(self._get_engine(), expire_on_commit=True)
        return self._async_sessionmaker

    def _get_engine(self) -> AsyncEngine:
        if self._engine is None:
            self._engine = create_async_engine(self._api_config.database_url, echo=self._api_config.echo_sql)
        return self._engine