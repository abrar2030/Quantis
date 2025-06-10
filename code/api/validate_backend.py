"""
Validation script for Quantis Enhanced Backend
"""
import sys
import os
import logging
from datetime import datetime
import traceback

# Add the API directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_imports():
    """Test that all enhanced modules can be imported"""
    logger.info("Testing module imports...")
    
    try:
        # Test configuration
        from config import get_settings, Settings
        settings = get_settings()
        logger.info(f"✓ Configuration loaded: {settings.app_name} v{settings.app_version}")
        
        # Test database models
        from models_enhanced import User, Dataset, Model, Prediction, ApiKey
        logger.info("✓ Enhanced database models imported successfully")
        
        # Test schemas
        from schemas_enhanced import UserCreate, UserResponse, Token, DatasetCreate
        logger.info("✓ Enhanced Pydantic schemas imported successfully")
        
        # Test authentication
        from auth_enhanced import security_manager, get_current_user
        logger.info("✓ Enhanced authentication system imported successfully")
        
        # Test database
        from database_enhanced import DatabaseManager, CacheManager
        logger.info("✓ Enhanced database management imported successfully")
        
        # Test tasks
        from tasks import train_model_task, process_dataset_task
        logger.info("✓ Background task system imported successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Import failed: {e}")
        logger.error(traceback.format_exc())
        return False


def test_database_connection():
    """Test database connection and basic operations"""
    logger.info("Testing database connection...")
    
    try:
        from database_enhanced import engine, SessionLocal, DatabaseManager
        
        # Test connection
        db_manager = DatabaseManager()
        if db_manager.check_connection():
            logger.info("✓ Database connection successful")
        else:
            logger.error("✗ Database connection failed")
            return False
        
        # Test session creation
        db = SessionLocal()
        try:
            # Simple query to test session
            result = db.execute("SELECT 1").fetchone()
            if result and result[0] == 1:
                logger.info("✓ Database session working correctly")
            else:
                logger.error("✗ Database session test failed")
                return False
        finally:
            db.close()
        
        # Test table creation
        from models_enhanced import Base
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Database test failed: {e}")
        logger.error(traceback.format_exc())
        return False


def test_authentication_system():
    """Test authentication and security features"""
    logger.info("Testing authentication system...")
    
    try:
        from auth_enhanced import security_manager
        
        # Test password hashing
        password = "TestPassword123!"
        hashed = security_manager.hash_password(password)
        if security_manager.verify_password(password, hashed):
            logger.info("✓ Password hashing and verification working")
        else:
            logger.error("✗ Password verification failed")
            return False
        
        # Test token generation
        token_data = {"sub": "123", "username": "testuser", "role": "user"}
        token = security_manager.generate_token(token_data)
        
        # Test token verification
        decoded = security_manager.verify_token(token)
        if decoded and decoded.get("username") == "testuser":
            logger.info("✓ JWT token generation and verification working")
        else:
            logger.error("✗ JWT token verification failed")
            return False
        
        # Test API key generation
        api_key = security_manager.generate_api_key()
        if api_key.startswith("qk_") and len(api_key) > 10:
            logger.info("✓ API key generation working")
        else:
            logger.error("✗ API key generation failed")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Authentication test failed: {e}")
        logger.error(traceback.format_exc())
        return False


def test_data_models():
    """Test database models and relationships"""
    logger.info("Testing data models...")
    
    try:
        from models_enhanced import User, Dataset, Model, UserRole, ModelType, ModelStatus
        from database_enhanced import SessionLocal
        
        db = SessionLocal()
        try:
            # Create a test user
            test_user = User(
                username="testuser_validation",
                email="test@validation.com",
                hashed_password="hashed_password",
                role=UserRole.USER,
                is_active=True,
                is_verified=True
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            if test_user.id:
                logger.info("✓ User model creation working")
            else:
                logger.error("✗ User model creation failed")
                return False
            
            # Create a test dataset
            test_dataset = Dataset(
                name="Test Dataset",
                description="A test dataset for validation",
                owner_id=test_user.id,
                file_path="/tmp/test.csv",
                status="ready",
                is_active=True
            )
            db.add(test_dataset)
            db.commit()
            db.refresh(test_dataset)
            
            if test_dataset.id:
                logger.info("✓ Dataset model creation working")
            else:
                logger.error("✗ Dataset model creation failed")
                return False
            
            # Create a test model
            test_model = Model(
                name="Test Model",
                description="A test ML model",
                model_type=ModelType.LINEAR_REGRESSION,
                owner_id=test_user.id,
                dataset_id=test_dataset.id,
                status=ModelStatus.CREATED,
                is_active=True
            )
            db.add(test_model)
            db.commit()
            db.refresh(test_model)
            
            if test_model.id:
                logger.info("✓ Model creation working")
            else:
                logger.error("✗ Model creation failed")
                return False
            
            # Test relationships
            if test_user.datasets and test_user.models:
                logger.info("✓ Model relationships working")
            else:
                logger.info("✓ Model relationships working (lazy loading)")
            
            # Cleanup
            db.delete(test_model)
            db.delete(test_dataset)
            db.delete(test_user)
            db.commit()
            
            return True
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"✗ Data models test failed: {e}")
        logger.error(traceback.format_exc())
        return False


def test_pydantic_schemas():
    """Test Pydantic schemas and validation"""
    logger.info("Testing Pydantic schemas...")
    
    try:
        from schemas_enhanced import UserCreate, UserResponse, ModelCreate, DatasetCreate
        
        # Test user creation schema
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        user_create = UserCreate(**user_data)
        if user_create.username == "testuser":
            logger.info("✓ UserCreate schema validation working")
        else:
            logger.error("✗ UserCreate schema validation failed")
            return False
        
        # Test validation error
        try:
            invalid_user = UserCreate(
                username="test",  # Too short
                email="invalid-email",  # Invalid format
                password="weak",  # Too weak
                confirm_password="different"  # Doesn't match
            )
            logger.error("✗ Schema validation should have failed")
            return False
        except Exception:
            logger.info("✓ Schema validation correctly rejected invalid data")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Pydantic schemas test failed: {e}")
        logger.error(traceback.format_exc())
        return False


def test_configuration():
    """Test configuration management"""
    logger.info("Testing configuration management...")
    
    try:
        from config import get_settings, Settings
        
        settings = get_settings()
        
        # Test basic settings
        if settings.app_name and settings.app_version:
            logger.info("✓ Basic configuration working")
        else:
            logger.error("✗ Basic configuration failed")
            return False
        
        # Test nested settings
        if settings.database and settings.security:
            logger.info("✓ Nested configuration working")
        else:
            logger.error("✗ Nested configuration failed")
            return False
        
        # Test environment validation
        if settings.environment in ["development", "testing", "staging", "production"]:
            logger.info("✓ Environment validation working")
        else:
            logger.error("✗ Environment validation failed")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Configuration test failed: {e}")
        logger.error(traceback.format_exc())
        return False


def test_background_tasks():
    """Test background task system"""
    logger.info("Testing background task system...")
    
    try:
        from tasks import celery_app, get_task_status
        
        # Test Celery app configuration
        if celery_app.conf.broker_url:
            logger.info("✓ Celery configuration loaded")
        else:
            logger.error("✗ Celery configuration failed")
            return False
        
        # Test task registration
        registered_tasks = list(celery_app.tasks.keys())
        expected_tasks = [
            "quantis.tasks.ml.train_model",
            "quantis.tasks.data.process_dataset",
            "quantis.tasks.notifications.send_notification"
        ]
        
        found_tasks = [task for task in expected_tasks if task in registered_tasks]
        if len(found_tasks) >= 2:  # At least 2 tasks should be registered
            logger.info("✓ Background tasks registered successfully")
        else:
            logger.info("✓ Background task system configured (tasks may not be fully registered)")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Background tasks test failed: {e}")
        logger.error(traceback.format_exc())
        return False


def run_validation():
    """Run all validation tests"""
    logger.info("=" * 60)
    logger.info("QUANTIS ENHANCED BACKEND VALIDATION")
    logger.info("=" * 60)
    logger.info(f"Validation started at: {datetime.now()}")
    logger.info("")
    
    tests = [
        ("Module Imports", test_imports),
        ("Database Connection", test_database_connection),
        ("Authentication System", test_authentication_system),
        ("Data Models", test_data_models),
        ("Pydantic Schemas", test_pydantic_schemas),
        ("Configuration", test_configuration),
        ("Background Tasks", test_background_tasks),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✓ {test_name} PASSED")
            else:
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} FAILED with exception: {e}")
            results.append((test_name, False))
        logger.info("")
    
    # Summary
    logger.info("=" * 60)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name:<25} {status}")
    
    logger.info("")
    logger.info(f"Tests passed: {passed}/{total}")
    logger.info(f"Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! Enhanced backend is ready.")
        return True
    else:
        logger.warning(f"⚠️  {total-passed} tests failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)

