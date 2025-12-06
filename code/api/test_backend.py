"""
Test script for Quantis API
"""

import os
import sys

# Add the API directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database

# Fix relative imports
import numpy as np
import pandas as pd
from services.dataset_service import DatasetService
from services.model_service import ModelService
from services.prediction_service import PredictionService
from services.user_service import UserService

from core.logging import get_logger

logger = get_logger(__name__)


def test_database_initialization():
    """Test database initialization"""
    logger.info("Testing database initialization...")
    try:
        database.init_db()
        logger.info("✓ Database initialized successfully")
        return True
    except Exception as e:
        logger.info(f"✗ Database initialization failed: {e}")
        return False


def test_user_service():
    """Test user service functionality"""
    logger.info("\nTesting user service...")
    db = database.SessionLocal()
    try:
        user_service = UserService(db)

        # Test user creation
        user = user_service.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="user",
        )
        logger.info(f"✓ Created user: {user.username} (ID: {user.id})")
        # Test authentication
        auth_user = user_service.authenticate_user("testuser", "testpass123")
        if auth_user:
            logger.info("✓ User authentication successful")
        else:
            logger.info("✗ User authentication failed")
            return False

        # Test API key creation
        api_key = user_service.create_api_key(user.id, "Test Key", 30)
        logger.info(f"✓ Created API key: {api_key[:10]}...")
        # Test API key validation
        key_info = user_service.validate_api_key(api_key)
        if key_info:
            logger.info("✓ API key validation successful")
        else:
            logger.info("✗ API key validation failed")
            return False

        return True

    except Exception as e:
        logger.info(f"✗ User service test failed: {e}")
        return False
    finally:
        db.close()


def test_dataset_service():
    """Test dataset service functionality"""
    logger.info("\nTesting dataset service...")
    db = database.SessionLocal()
    try:
        dataset_service = DatasetService(db)

        # Create sample data
        sample_data = pd.DataFrame(
            {
                "timestamp": pd.date_range("2023-01-01", periods=100, freq="D"),
                "value": np.random.randn(100).cumsum(),
                "feature1": np.random.randn(100),
                "feature2": np.random.randint(0, 10, 100),
            }
        )

        # Test dataset creation
        dataset = dataset_service.create_dataset(
            name="Test Dataset",
            description="A test time series dataset",
            owner_id=1,  # Assuming admin user exists
            data=sample_data,
        )
        logger.info(f"✓ Created dataset: {dataset.name} (ID: {dataset.id})")
        logger.info(f"  - Rows: {dataset.row_count}")
        logger.info(
            f"  - Columns: {len(dataset.columns_info['columns']) if dataset.columns_info else 0}"
        )
        # Test dataset statistics
        stats = dataset_service.get_dataset_statistics(dataset.id)
        if stats:
            logger.info("✓ Dataset statistics calculated successfully")
        else:
            logger.info("✗ Dataset statistics calculation failed")
            return False

        return True

    except Exception as e:
        logger.info(f"✗ Dataset service test failed: {e}")
        return False
    finally:
        db.close()


def test_model_service():
    """Test model service functionality"""
    logger.info("\nTesting model service...")
    db = database.SessionLocal()
    try:
        model_service = ModelService(db)

        # Test model creation
        model = model_service.create_model(
            name="Test TFT Model",
            description="A test Temporal Fusion Transformer model",
            model_type="tft",
            owner_id=1,  # Assuming admin user exists
            dataset_id=1,  # Assuming dataset exists
            hyperparameters={"epochs": 100, "learning_rate": 0.001},
        )
        logger.info(f"✓ Created model: {model.name} (ID: {model.id})")
        logger.info(f"  - Type: {model.model_type}")
        logger.info(f"  - Status: {model.status}")
        # Test model training
        success = model_service.train_dummy_model(model.id)
        if success:
            logger.info("✓ Model training completed successfully")
            # Check if model was saved
            trained_model = model_service.load_trained_model(model.id)
            if trained_model:
                logger.info("✓ Trained model loaded successfully")
            else:
                logger.info("✗ Failed to load trained model")
                return False
        else:
            logger.info("✗ Model training failed")
            return False

        return True

    except Exception as e:
        logger.info(f"✗ Model service test failed: {e}")
        return False
    finally:
        db.close()


def test_prediction_service():
    """Test prediction service functionality"""
    logger.info("\nTesting prediction service...")
    db = database.SessionLocal()
    try:
        prediction_service = PredictionService(db)

        # Test single prediction
        input_data = [1.0, 2.0, 3.0, 4.0, 5.0]
        prediction = prediction_service.create_prediction(
            user_id=1,  # Assuming admin user exists
            model_id=1,  # Assuming trained model exists
            input_data=input_data,
        )
        logger.info(f"✓ Created prediction: {prediction.id}")
        logger.info(f"  - Result: {prediction.prediction_result}")
        logger.info(f"  - Confidence: {prediction.confidence_score:.3f}")
        logger.info(f"  - Execution time: {prediction.execution_time_ms}ms")
        # Test batch predictions
        batch_input = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
        batch_predictions = prediction_service.batch_predict(
            user_id=1, model_id=1, input_data_list=batch_input
        )
        logger.info(
            f"✓ Created batch predictions: {len(batch_predictions)} predictions"
        )
        # Test prediction statistics
        stats = prediction_service.get_prediction_statistics(user_id=1)
        logger.info(
            f"✓ Prediction statistics: {stats['total_predictions']} total predictions"
        )
        return True

    except Exception as e:
        logger.info(f"✗ Prediction service test failed: {e}")
        return False
    finally:
        db.close()


def main():
    """Run all tests"""
    logger.info("=" * 50)
    logger.info("Quantis API Backend Test Suite")
    logger.info("=" * 50)
    tests = [
        test_database_initialization,
        test_user_service,
        test_dataset_service,
        test_model_service,
        test_prediction_service,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    logger.info("\n" + "=" * 50)
    logger.info(f"Test Results: {passed}/{total} tests passed")
    if passed == total:
        logger.info("🎉 All tests passed! The backend is working correctly.")
        return True
    else:
        logger.info("❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
