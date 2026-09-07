from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config.settings import DATABASE_URL, DB_ECHO, DB_MAX_OVERFLOW, DB_POOL_SIZE


# 创建异步引擎
async_engine = create_async_engine(
 DATABASE_URL,
 echo=DB_ECHO, # 可选：输出SQL⽇志
 pool_size=DB_POOL_SIZE, # 设置连接池中保持的持久连接数
 max_overflow=DB_MAX_OVERFLOW # 设置连接池允许创建的额外连接数
)
# 创建异步会话⼯⼚
AsyncSessionLocal = async_sessionmaker(
 bind=async_engine,
 class_=AsyncSession,
 expire_on_commit=False
)
# 依赖项，⽤于获取数据库会话
async def get_db():
 async with AsyncSessionLocal() as session:
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
