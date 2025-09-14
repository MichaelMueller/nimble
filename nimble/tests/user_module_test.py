# builtin
import os, sys
from typing_extensions import Literal, Optional, Type, Set
# 3rd party
import pytest
from sqlalchemy.ext.asyncio import AsyncConnection
# local
project_path = os.path.abspath( os.path.dirname( __file__) + "/../.." )
if not project_path in sys.path:
    sys.path.insert(0, project_path)
from nimble import UserModule, UserCreate, Api, UserSelect, UserDescriptor, In, Eq

class UserModuleTest:

    def setup_method(self):
        pass

    @pytest.mark.asyncio
    async def test(self):
        api = Api()
        await api.register_module(UserModule)
        user_id = await api.execute( UserCreate(username="testuser", email="testuser@example.com", password="securepassword") )
        user_id = await api.execute( UserCreate(username="testuser2", email="testuser2@example.com", password="securepassword2") )
        user_id = await api.execute( UserCreate(username="testuser3", email="testuser3@example.com", password="securepassword3") )
        user_id = await api.execute( UserCreate(username="testuser4", email="testuser4@example.com", password="securepassword4") )
        user_id = await api.execute( UserCreate(username="testuser5", email="testuser5@example.com", password="securepassword5") )
        assert user_id == 5
        user_id_descriptor = UserDescriptor( id=In( values=[1,3] ) )
        user_name_descriptor = UserDescriptor( username=Eq( value="testuser2" ) )
        
        users = await api.execute( UserSelect(descriptors=[user_id_descriptor, user_name_descriptor]) )
        assert len(users) == 3
        
if __name__ == "__main__":
    # Run pytest against *this* file only
    sys.exit(pytest.main([__file__, "--no-cov"]))