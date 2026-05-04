from fastapi import FastAPI, Response
from pydantic import BaseModel
import uvicorn
from prometheus_client import generate_latest, Counter

app = FastAPI()


class MachineFeatures(BaseModel):
    Air_Temperature: float
    Process_Temperature: float
    Rotational_Speed: float
    Torque: float
    Tool_Wear: float

# --- PROMETHEUS METRICS ---
# 1. Total requests count
REQUEST_COUNT = Counter('request_count', 'App Request Count', ['endpoint'])

# 2. Accuracy track karne ke liye
TOTAL_PREDICTIONS = Counter('model_total_predictions', 'Total number of model predictions')
CORRECT_PREDICTIONS = Counter('model_correct_predictions', 'Number of correct model predictions')

@app.get("/")
def home():
    REQUEST_COUNT.labels(endpoint='/').inc()
    return {"status": "success", "message": "Industrial Predictive Maintenance API is Live!"}

@app.post("/predict")
def predict(features: MachineFeatures):
    REQUEST_COUNT.labels(endpoint='/predict').inc()
    
    
    if features.Tool_Wear > 200 and features.Torque > 45:
        prediction_result = 1  # Machine Failure
    else:
        prediction_result = 0  # Machine Normal
    
    return {
        "status": "success",
        "message": "Prediction successful!",
        "Machine_Failure": prediction_result,
        "input_data": features.model_dump()
    }

# --- NEW FEEDBACK ENDPOINT ---
@app.post("/feedback")
def feedback(is_correct: bool):
    """
    User batayega ke model ki prediction sahi thi ya nahi.
    Example: POST /feedback?is_correct=true
    """
    REQUEST_COUNT.labels(endpoint='/feedback').inc()
    TOTAL_PREDICTIONS.inc()
    
    if is_correct:
        CORRECT_PREDICTIONS.inc()
    
    return {"status": "feedback received", "is_correct": is_correct}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)