import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import mlflow
from .mlflow_tracking import log_experiment, register_model

class TimeSeriesModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, num_layers=2):
        super(TimeSeriesModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layer
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2
        )
        
        # Fully connected layer
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        # Initialize hidden state with zeros
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        # Forward propagate LSTM
        out, _ = self.lstm(x, (h0, c0))
        
        # Get the output from the last time step
        out = self.fc(out[:, -1, :])
        return out

def train_model(data_path, params=None):
    """
    Train a time series forecasting model
    
    Args:
        data_path: Path to processed data
        params: Dictionary of hyperparameters
    
    Returns:
        Trained model
    """
    # Default parameters
    if params is None:
        params = {
            'input_size': 10,
            'hidden_size': 64,
            'output_size': 3,
            'num_layers': 2,
            'learning_rate': 0.001,
            'batch_size': 32,
            'epochs': 100
        }
    
    # Load data (in a real scenario, this would load from data_path)
    # For this example, we'll create dummy data
    X = np.random.randn(1000, 24, params['input_size'])  # 1000 samples, 24 time steps, 10 features
    y = np.random.randn(1000, params['output_size'])     # 1000 samples, 3 output values
    
    # Convert to PyTorch tensors
    X_tensor = torch.FloatTensor(X)
    y_tensor = torch.FloatTensor(y)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X_tensor, y_tensor, test_size=0.2, random_state=42)
    
    # Create model
    model = TimeSeriesModel(
        input_size=params['input_size'],
        hidden_size=params['hidden_size'],
        output_size=params['output_size'],
        num_layers=params['num_layers']
    )
    
    # Loss and optimizer
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=params['learning_rate'])
    
    # Training loop
    for epoch in range(params['epochs']):
        # Forward pass
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        
        # Backward and optimize
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if (epoch+1) % 10 == 0:
            print(f'Epoch [{epoch+1}/{params["epochs"]}], Loss: {loss.item():.4f}')
    
    # Evaluate model
    model.eval()
    with torch.no_grad():
        y_pred = model(X_test)
        test_loss = criterion(y_pred, y_test)
        
        # Convert to numpy for sklearn metrics
        y_test_np = y_test.numpy()
        y_pred_np = y_pred.numpy()
        
        mse = mean_squared_error(y_test_np, y_pred_np)
        mae = mean_absolute_error(y_test_np, y_pred_np)
        r2 = r2_score(y_test_np, y_pred_np)
    
    print(f'Test Loss: {test_loss.item():.4f}')
    print(f'MSE: {mse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f}')
    
    # Log metrics with MLflow
    metrics = {
        'mse': mse,
        'mae': mae,
        'r2': r2
    }
    
    # Create a simple wrapper class for sklearn compatibility
    class ModelWrapper:
        def __init__(self, model):
            self.model = model
            
        def predict(self, X):
            X_tensor = torch.FloatTensor(X)
            self.model.eval()
            with torch.no_grad():
                return self.model(X_tensor).numpy()
                
        def predict_proba(self, X):
            # This is a regression model, but we'll return dummy probabilities
            # for compatibility with the API
            preds = self.predict(X)
            # Convert to probabilities (dummy implementation)
            probs = np.abs(preds) / np.sum(np.abs(preds), axis=1, keepdims=True)
            return probs
    
    # Wrap the PyTorch model
    wrapped_model = ModelWrapper(model)
    
    # Save the model
    model_path = os.path.join(os.path.dirname(__file__), 'tft_model.pkl')
    joblib.dump(wrapped_model, model_path)
    
    # Log with MLflow
    try:
        log_experiment(params, metrics, model)
        register_model("time_series_forecaster", mlflow.active_run().info.run_id)
    except Exception as e:
        print(f"MLflow logging failed: {e}")
    
    return wrapped_model

if __name__ == "__main__":
    train_model(None)
