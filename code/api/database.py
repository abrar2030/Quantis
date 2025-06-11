"""
Enhanced database configuration and management for Quantis API
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from sqlalchemy import create_engine, event, pool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine
import redis.asyncio as redis
from redis.asyncio import Redis

from .config import get_settings
from .models import Base

logger = logging.getLogger(__name__)
settings = get_settings()

# Synchronous database engine
engine = create_engine(
    settings.database.url,
    echo=settings.database.echo,
    poolclass=QueuePool,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_timeout=settings.database.pool_timeout,
    pool_recycle=settings.database.pool_recycle,
    pool_pre_ping=True,  # Verify connections before use
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis connection
redis_client: Optional[Redis] = None


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance and reliability"""
    if "sqlite" in settings.database.url:
        cursor = dbapi_connection.cursor()
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys=ON")
        # Set journal mode to WAL for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        # Set synchronous mode to NORMAL for better performance
        cursor.execute("PRAGMA synchronous=NORMAL")
        # Set cache size to 64MB
        cursor.execute("PRAGMA cache_size=-64000")
        cursor.close()


@event.listens_for(Engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log database connection checkout"""
    logger.debug("Database connection checked out")


@event.listens_for(Engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log database connection checkin"""
    logger.debug("Database connection checked in")


def init_db():
    """Initialize database tables"""
    try:
        logger.info("Initializing database...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db() -> Session:
    """Get database session dependency"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def get_redis() -> Redis:
    """Get Redis client dependency"""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.redis.url,
            max_connections=settings.redis.max_connections,
            socket_timeout=settings.redis.socket_timeout,
            socket_connect_timeout=settings.redis.socket_connect_timeout,
            decode_responses=True,
        )
    return redis_client


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


class DatabaseManager:
    """Database management utilities"""
    
    @staticmethod
    def create_tables():
        """Create all database tables"""
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def drop_tables():
        """Drop all database tables"""
        Base.metadata.drop_all(bind=engine)
    
    @staticmethod
    def get_table_info():
        """Get information about database tables"""
        inspector = engine.inspect(engine)
        tables = {}
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            tables[table_name] = {
                "columns": [col["name"] for col in columns],
                "column_info": columns
            }
        return tables
    
    @staticmethod
    def check_connection():
        """Check database connection health"""
        try:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
    
    @staticmethod
    def get_connection_info():
        """Get database connection information"""
        pool = engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid(),
        }


class CacheManager:
    """Redis cache management utilities"""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            return await self.redis.set(key, value, ex=expire)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return bool(await self.redis.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(await self.redis.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in cache"""
        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key"""
        try:
            return await self.redis.expire(key, seconds)
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False
    
    async def get_keys(self, pattern: str) -> list:
        """Get keys matching pattern"""
        try:
            return await self.redis.keys(pattern)
        except Exception as e:
            logger.error(f"Cache keys error for pattern {pattern}: {e}")
            return []
    
    async def flush_db(self) -> bool:
        """Flush all keys from current database"""
        try:
            return await self.redis.flushdb()
        except Exception as e:
            logger.error(f"Cache flush error: {e}")
            return False


class TransactionManager:
    """Database transaction management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def __enter__(self):
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.rollback()
        else:
            self.db.commit()


@asynccontextmanager
async def get_cache_manager() -> AsyncGenerator[CacheManager, None]:
    """Get cache manager with automatic cleanup"""
    redis_client = await get_redis()
    cache_manager = CacheManager(redis_client)
    try:
        yield cache_manager
    finally:
        # Redis connection is managed globally, no need to close here
        pass


def create_database_url(
    driver: str = "postgresql",
    username: str = "quantis",
    password: str = "password",
    host: str = "localhost",
    port: int = 5432,
    database: str = "quantis"
) -> str:
    """Create database URL from components"""
    return f"{driver}://{username}:{password}@{host}:{port}/{database}"


def migrate_database():
    """Run database migrations"""
    # This would typically use Alembic for migrations
    # For now, we'll just create tables
    try:
        logger.info("Running database migrations...")
        init_db()
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        raise


def health_check() -> dict:
    """Perform comprehensive health check"""
    health_status = {
        "database": False,
        "redis": False,
        "timestamp": None
    }
    
    # Check database
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        health_status["database"] = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    # Check Redis
    try:
        import asyncio
        async def check_redis():
            redis_client = await get_redis()
            await redis_client.ping()
            return True
        
        health_status["redis"] = asyncio.run(check_redis())
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
    
    from datetime import datetime
    health_status["timestamp"] = datetime.utcnow().isoformat()
    
    return health_status

