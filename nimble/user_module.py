# builtin
from typing import Optional, Any, Set, Type, TYPE_CHECKING
# 3rd party
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncConnection
from sqlalchemy import Table, Column, Integer, String, MetaData
# local
if TYPE_CHECKING:
    from nimble.api import Api
from nimble.module import Module, Query
from nimble.user_create import UserCreate
from nimble.user_select import UserSelect

class UserModule(Module):

    def __init__(self, api: "Api"):
        super().__init__(api)
        self._initialized: bool = False
        self._users_table: Optional[Table] = None
    
    async def _initialize(self, db:AsyncConnection) -> None:
        metadata = MetaData()
        self._users_table = Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("username", String(255), nullable=False, unique=True),
            Column("email", String(255), nullable=False, unique=True),
            Column("password", String(255), nullable=False),
        )
        await db.run_sync(metadata.create_all)
        self._initialized = True
          
    def get_executable_queries(self) -> Set[Type["Query"]]:
        return {UserCreate, UserSelect}
    
    async def execute(self, query:Query, db:AsyncConnection) -> int | list[tuple]:
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