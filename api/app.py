from fastapi import FastAPI  
from pydantic import BaseModel  
import joblib  

app = FastAPI()  
model = joblib.load("tft_model.pkl")  

class PredictionRequest(BaseModel):  
    features: list  
    api_key: str  

@app.post("/predict")  
async def predict(request: PredictionRequest):  
    return {  
        "prediction": model.predict([request.features]).tolist(),  
        "confidence": model.predict_proba([request.features]).max()  
    }  

@app.get("/model_health")  
def health_check():  
    return {"status": "healthy", "version": "2.1.0"}  