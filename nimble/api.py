# builtin
from typing import Optional, Union, Set, Callable, Type, Any, Literal, TYPE_CHECKING, Dict, List, Tuple
import logging
# 3rd party
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection, AsyncEngine
# local
from nimble.module import Module
from nimble.query import Query
from nimble.api_config import ApiConfig
from nimble.unprocessable_query_exception import UnprocessableQueryException

class Api:
    def __init__(self, config:Optional[ApiConfig]=None, engine:Optional[AsyncEngine]=None):       
        self._api_config = config or ApiConfig()
        # state 
        self._modules:Dict[Type[Module], Module] = {}
        # db
        self._db_initialized: bool = False
        self._engine: Optional[AsyncEngine] = None
        
    def clone(self) -> "Api":
        clone = Api(config=self._api_config.model_copy(deep=True), engine=self._get_engine())
        for module in self._modules:
            clone.register_module(module.__class__)
        return clone

    async def register_module(self, module_class:Type[Module]) -> None:                     
        # check unique query type processor
        module:Module = module_class()              
        for qtype in module.processable_queries():
            for existing_module in self._modules.values():
                if qtype in existing_module.processable_queries():
                    raise KeyError(f"Query type {qtype.__name__} is already registered by module {existing_module.__class__.__name__}")

        self._modules[module.__class__] = module

        engine = self._get_engine()
        async with engine.begin() as conn:
            await module.initialize(self, conn if self._db_initialized is False else None)            

    async def unregister_module(self, module_class:Type[Module]) -> None:        
        module = self._modules.pop(module_class)
        
        engine = self._get_engine()
        async with engine.begin() as conn:
            await module.shutdown(self, conn if self._db_initialized is False else None)

    async def execute(self, query:"Query") -> Any: 
        qtype = type(query)
        # for the hooks: consider all subclasses of the query type
        qtype_mros = [t for t in qtype.__mro__ if issubclass(t, Query)]
        
        # collect relevant modules
        processor_module:Optional[Module] = None
        pre_process_modules: Set[Module] = set()
        post_process_modules: Set[Module] = set()
        
        for module in self._modules.values():
            
            if qtype in module.processable_queries():
                processor_module = module
                
            for qtype_mro in qtype_mros:
                if qtype_mro in module.pre_processable_queries():
                    pre_process_modules.add(module)
                if qtype_mro in module.post_processable_queries():
                    post_process_modules.add(module)
            
        if processor_module is None:
            raise UnprocessableQueryException(f"No module registered to handle query of type {qtype.__name__}")
        
        # run the query
        async with self._engine.begin() as db:

            # pre process
            for m in pre_process_modules:
                await m.pre_process(self, query, db)
                    
            result = await processor_module.process(self, query, db)

            # post process
            for m in post_process_modules:
                await m.post_process(self, query, db, result)

            return result

    async def shutdown(self) -> None:        
        for module_type in list( self._modules.keys() ).copy():
            try:
                await self.unregister_module(module_type)
            except Exception as e:
                logging.error(f"Error shutting down module {module_type.__name__}: {e}")

        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
    
    def _get_engine(self) -> AsyncEngine:
        if self._engine is None:
            self._engine = create_async_engine(self._api_config.database_url, echo=self._api_config.echo_sql)
        return self._engine
    