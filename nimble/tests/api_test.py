# builtin
import os, sys
from typing_extensions import Literal, Optional, Type, Set
# 3rd party
import pytest
# local
project_path = os.path.abspath( os.path.dirname( __file__) + "/../.." )
if not project_path in sys.path:
    sys.path.insert(0, project_path)
from nimble.api import Api, Module, Query, AsyncSession, AsyncConnection

class ApiTest:

    def setup_method(self):
        pass

    @pytest.mark.asyncio
    async def test(self):
        class HelloQuery(Query):
            type:Literal["hello_query"] = "hello_query"
            
        class TestModule(Module):
            def __init__(self, api):
                super().__init__(api)
                self.num_initializes = 0
                self.num_pre_executes = 0
                self.num_executes = 0     
                self.num_post_executes = 0     
                self.num_shutdowns = 0  
            
            async def _initialize(self, db:AsyncConnection) -> None:
                self.num_initializes += 1

            async def _shutdown(self, db:AsyncConnection) -> None:
                self.num_shutdowns += 1

            def get_executable_queries(self) -> Set[Type[Query]]:
                return { HelloQuery }
            
            async def execute(self, query:Query, db:AsyncSession) -> int:
                self.num_executes += 1
                return self.num_executes
            
            def pre_execute_for(self) -> Set[Type[Query]]:
                return { HelloQuery }

            async def pre_execute(self, query:Query, db:AsyncSession) -> None:
                self.num_pre_executes += 1
                
            def post_execute_for(self) -> Set[Type[Query]]:
                return { HelloQuery }

            async def post_execute(self, query:Query, db:AsyncSession, result:int) -> None:
                self.num_post_executes += 1
            
        class ModuleWithShutdownException(Module):
            def get_executable_queries(self) -> Set[Type[Query]]:
                return {None}
            
            async def _shutdown(self, db):
                raise NotImplementedError()
            
        module = Module(None)
        with pytest.raises(NotImplementedError):
            module.get_executable_queries()
        with pytest.raises(NotImplementedError):
            await module.execute( HelloQuery(), None )
        assert module.api() == None
        assert module.pre_execute_for() == set()
        assert module.post_execute_for() == set()
        assert await module._initialize( None ) == None
        assert await module._shutdown( None ) == None
        assert await module.pre_execute( HelloQuery(), None ) == None
        assert await module.post_execute( HelloQuery(), None, None ) == None
            
        api = Api()
        module:TestModule = await api.register_module( TestModule )
        await api.unregister_module( module )
        assert module.num_initializes == 1
        assert module.num_shutdowns == 1
        assert module.num_executes == 0
        
        module:TestModule = await api.register_module( TestModule )
        result = await api.execute( HelloQuery() )
        assert result == 1
        assert module.num_initializes == 1
        assert module.num_shutdowns == 0
        assert module.num_executes == 1
        assert module.num_pre_executes == 1
        assert module.num_post_executes == 1
        
        await api.shutdown()
        assert module.num_shutdowns == 1
        
        with pytest.raises(ValueError):
            await api.execute( HelloQuery() )
        
        await api.register_module( TestModule )
        with pytest.raises(ValueError):
            await api.register_module( TestModule )    
        await api.register_module( ModuleWithShutdownException )

        await api.shutdown()  # should not raise
        
if __name__ == "__main__":
    # Run pytest against *this* file only
    sys.exit(pytest.main([__file__, "--no-cov"]))