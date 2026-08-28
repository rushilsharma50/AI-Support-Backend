from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Create the async engine for PostgreSQL
# We use asyncpg for non-blocking database operations, which works perfectly with FastAPI
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# Session factory for creating database sessions
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Dependency to inject the database session into FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
