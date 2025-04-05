import pytest  
import torch  

def test_model_loading():  
    model = TemporalFusionTransformer(input_size=128)  
    model.load_state_dict(torch.load("tft_model.pt"))  
    assert model(torch.randn(1, 128)).shape == (1, 1)  

def test_api_endpoint(test_client):  
    response = test_client.post("/predict", json={  
        "features": [0.1, 0.5, ...],  
        "api_key": "valid_key"  
    })  
    assert response.status_code == 200  