"""
Database configuration and connection management
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from models import Base

# Database URL - use SQLite for development, can be easily changed to PostgreSQL/MySQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./quantis.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
    )
else:
    engine = create_engine(
        DATABASE_URL,
        echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database with default data"""
    from models import User, ApiKey
    from services.user_service import UserService
    
    create_tables()
    
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin_user = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin_user:
            # Create default admin user
            user_service = UserService(db)
            admin_user = user_service.create_user(
                username="admin",
                email="admin@quantis.com",
                password="admin123",  # Change this in production!
                role="admin"
            )
            print(f"Created admin user with ID: {admin_user.id}")
            
            # Create default API key for admin
            api_key = user_service.create_api_key(
                user_id=admin_user.id,
                name="Default Admin Key",
                expires_days=365
            )
            print(f"Created admin API key: {api_key}")
        
        # Check if demo user exists
        demo_user = db.query(models.User).filter(models.User.username == "demo").first()
        if not demo_user:
            user_service = UserService(db)
            demo_user = user_service.create_user(
                username="demo",
                email="demo@quantis.com",
                password="demo123",
                role="user"
            )
            print(f"Created demo user with ID: {demo_user.id}")
            
            # Create API key for demo user
            api_key = user_service.create_api_key(
                user_id=demo_user.id,
                name="Demo User Key",
                expires_days=30
            )
            print(f"Created demo API key: {api_key}")
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

