# builtin
import os, sys
from typing_extensions import Literal, Optional, Type, Set, Any
# 3rd party
import pytest
# local
project_path = os.path.abspath( os.path.dirname( __file__) + "/../.." )
if not project_path in sys.path:
    sys.path.insert(0, project_path)
from nimble.module import Module, Query, AsyncConnection, AsyncConnection, QuerySet
from nimble.api import Api
from nimble.unprocessable_query_exception import UnprocessableQueryException
from sqlalchemy import Table, Column, Integer, String, MetaData

class ApiTest:

    def setup_method(self):
        pass

    @pytest.mark.asyncio
    async def test(self):
        class HelloQuery(Query):
            type:Literal["hello_query"] = "hello_query"
            
        class TestModule(Module):
            num_initializes:int = 0
            num_shutdowns:int = 0
            num_processes:int = 0
            num_pre_processes:int = 0
            num_post_processes:int = 0
                                                
            async def initialize(self, api:"Api", db:Optional[AsyncConnection]) -> None:
                TestModule.num_initializes += 1          

            async def shutdown(self, api:"Api", db:Optional[AsyncConnection]) -> None:
                TestModule.num_shutdowns += 1

            def pre_processable_queries(self) -> QuerySet:
                return { HelloQuery }

            async def pre_process(self, api:"Api", query:Query, db:AsyncConnection) -> None:
                TestModule.num_pre_processes += 1
                
            def processable_queries(self) -> QuerySet:
                return { HelloQuery }
            
            async def process(self, api:"Api", query:Query, db:AsyncConnection) -> int:
                TestModule.num_processes += 1
                return TestModule.num_processes
                
            def post_processable_queries(self) -> QuerySet:
                return { HelloQuery }

            async def post_process(self, api:"Api", query:Query, db:AsyncConnection, result:int) -> None:
                TestModule.num_post_processes += 1
                
        class ModuleWithShutdownException(Module):
            def processable_queries(self) -> Set[Type[Query]]:
                return {HelloQuery}
            
            async def _shutdown(self, db):
                raise NotImplementedError()
            
        api = Api()
        await api.register_module( TestModule )
        await api.unregister_module( TestModule )
        assert TestModule.num_initializes == 1
        assert TestModule.num_shutdowns == 1
        assert TestModule.num_processes == 0
        
        await api.register_module( TestModule )
        result = await api.execute( HelloQuery() )
        assert result == 1
        assert TestModule.num_initializes == 2
        assert TestModule.num_shutdowns == 1
        assert TestModule.num_processes == 1
        assert TestModule.num_pre_processes == 1
        assert TestModule.num_post_processes == 1
        
        await api.shutdown()
        assert TestModule.num_shutdowns == 2
        
        with pytest.raises(UnprocessableQueryException):
            await api.execute( HelloQuery() )
        
        await api.register_module( TestModule )
        with pytest.raises(KeyError):
            await api.register_module( TestModule )  
        await api.unregister_module( TestModule )  
        await api.register_module( ModuleWithShutdownException )

        await api.shutdown()  # should not raise
        
if __name__ == "__main__":
    # Run pytest against *this* file only
    sys.exit(pytest.main([__file__, "--no-cov"]))