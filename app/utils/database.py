from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.utils.settings import settings


# 비동기 데이터베이스 엔진
db_engine = create_async_engine(
    url=f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}",
    echo=settings.DB_ECHO,
)

# 세션 팩토리
AsyncSessionFactory = async_sessionmaker(db_engine, class_=AsyncSession)

# Base 클래스
Base = declarative_base()

# 세션 의존성
async def get_db():
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            session.close()