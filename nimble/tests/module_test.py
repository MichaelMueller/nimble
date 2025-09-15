# builtin
import os, sys
# 3rd party
import pytest
# local
project_path = os.path.abspath( os.path.dirname( __file__) + "/../.." )
if not project_path in sys.path:
    sys.path.insert(0, project_path)
from nimble.module import Module

class ModuleTest:

    @pytest.mark.asyncio
    async def test(self):
        m = Module()
        await m.initialize(None, None)
        await m.shutdown(None, None)
        assert m.pre_processable_queries() == set()
        await m.pre_process(None, None, None)
        with pytest.raises(NotImplementedError):
            m.processable_queries()
        with pytest.raises(NotImplementedError):
            await m.process(None, None, None)
        assert m.post_processable_queries() == set()
        await m.post_process(None, None, None, None)
         
        
if __name__ == "__main__":
    # Run pytest against *this* file only
    sys.exit(pytest.main([__file__, "--no-cov"]))