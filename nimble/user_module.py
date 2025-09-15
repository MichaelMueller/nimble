# builtin
from typing import Optional, Any, Set, Type, TYPE_CHECKING
# 3rd party
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncConnection
from sqlalchemy import Table, Column, Integer, String, MetaData
# local
if TYPE_CHECKING:
    from nimble.api import Api
from nimble.user import User
from nimble.module import Module, Query
from nimble.user_create import UserCreate
from nimble.user_select import UserSelect

class UserModule(Module):

    def __init__(self):
        self._users_table: Optional[Table] = None
            
    async def initialize(self, api:"Api", db:Optional[AsyncConnection]) -> None:
        if db is None:
            return
        metadata, self._users_table = User.to_sqlalchemy_table()
        await db.run_sync(metadata.create_all)
          
    def processable_queries(self) -> Set[Type["Query"]]:
        return { UserCreate, UserSelect }
    
    async def process(self, api:"Api", query:Query, db:AsyncConnection) -> int | list[tuple]:
        if isinstance(query, UserCreate):
            insert_stmt = self._users_table.insert().values(
                username=query.username,
                email=query.email,
                password=query.password
            )
            result = await db.execute(insert_stmt)
            return result.inserted_primary_key[0]
            
        elif isinstance(query, UserSelect):
            select_stmt = self._users_table.select()
            expression = query.to_bool_expression(self._users_table)
            if expression is not None:
                select_stmt = select_stmt.where(expression)
                    
            result = await db.execute(select_stmt)
            rows = result.fetchall()
            return rows