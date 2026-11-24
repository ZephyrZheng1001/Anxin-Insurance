from sqlalchemy import text

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from typing_extensions import AsyncGenerator

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

if not settings.db or not settings.db.url:
    raise RuntimeError("db.url未配置，初始化数据库失败！")
DATABASE_URL = settings.db.url

# 创建异步数据库引擎
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo = settings.db.echo,
    pool_size = settings.db.pool_size,
    max_overflow = settings.db.max_overflow,
    pool_recycle = settings.db.pool_recycle,
    pool_pre_ping = True,
)

# 创建异步 Session 工厂
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """为每个 FastAPI 请求创建独立的 AsyncSession，适用于依赖注入"""
    async with AsyncSessionFactory() as session:
        yield session


async def close_database() -> None:
   await engine.dispose()
   logger.info("数据库连接池已关闭")

# 数据库健康检查
async def check_database() -> None:
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    logger.info("数据库连接池初始化成功")
