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


def test_database_initialization():
    """Test database initialization"""
    print("Testing database initialization...")
    try:
        database.init_db()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False


def test_user_service():
    """Test user service functionality"""
    print("\nTesting user service...")
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
        print(f"✓ Created user: {user.username} (ID: {user.id})")

        # Test authentication
        auth_user = user_service.authenticate_user("testuser", "testpass123")
        if auth_user:
            print("✓ User authentication successful")
        else:
            print("✗ User authentication failed")
            return False

        # Test API key creation
        api_key = user_service.create_api_key(user.id, "Test Key", 30)
        print(f"✓ Created API key: {api_key[:10]}...")

        # Test API key validation
        key_info = user_service.validate_api_key(api_key)
        if key_info:
            print("✓ API key validation successful")
        else:
            print("✗ API key validation failed")
            return False

        return True

    except Exception as e:
        print(f"✗ User service test failed: {e}")
        return False
    finally:
        db.close()


def test_dataset_service():
    """Test dataset service functionality"""
    print("\nTesting dataset service...")
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
        print(f"✓ Created dataset: {dataset.name} (ID: {dataset.id})")
        print(f"  - Rows: {dataset.row_count}")
        print(
            f"  - Columns: {len(dataset.columns_info['columns']) if dataset.columns_info else 0}"
        )

        # Test dataset statistics
        stats = dataset_service.get_dataset_statistics(dataset.id)
        if stats:
            print("✓ Dataset statistics calculated successfully")
        else:
            print("✗ Dataset statistics calculation failed")
            return False

        return True

    except Exception as e:
        print(f"✗ Dataset service test failed: {e}")
        return False
    finally:
        db.close()


def test_model_service():
    """Test model service functionality"""
    print("\nTesting model service...")
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
        print(f"✓ Created model: {model.name} (ID: {model.id})")
        print(f"  - Type: {model.model_type}")
        print(f"  - Status: {model.status}")

        # Test model training
        success = model_service.train_dummy_model(model.id)
        if success:
            print("✓ Model training completed successfully")

            # Check if model was saved
            trained_model = model_service.load_trained_model(model.id)
            if trained_model:
                print("✓ Trained model loaded successfully")
            else:
                print("✗ Failed to load trained model")
                return False
        else:
            print("✗ Model training failed")
            return False

        return True

    except Exception as e:
        print(f"✗ Model service test failed: {e}")
        return False
    finally:
        db.close()


def test_prediction_service():
    """Test prediction service functionality"""
    print("\nTesting prediction service...")
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
        print(f"✓ Created prediction: {prediction.id}")
        print(f"  - Result: {prediction.prediction_result}")
        print(f"  - Confidence: {prediction.confidence_score:.3f}")
        print(f"  - Execution time: {prediction.execution_time_ms}ms")

        # Test batch predictions
        batch_input = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
        batch_predictions = prediction_service.batch_predict(
            user_id=1, model_id=1, input_data_list=batch_input
        )
        print(f"✓ Created batch predictions: {len(batch_predictions)} predictions")

        # Test prediction statistics
        stats = prediction_service.get_prediction_statistics(user_id=1)
        print(
            f"✓ Prediction statistics: {stats['total_predictions']} total predictions"
        )

        return True

    except Exception as e:
        print(f"✗ Prediction service test failed: {e}")
        return False
    finally:
        db.close()


def main():
    """Run all tests"""
    print("=" * 50)
    print("Quantis API Backend Test Suite")
    print("=" * 50)

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

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The backend is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
