# app/main.py
from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel

app = FastAPI()

# Define a more accurate name for the input data structure
class EyeTrackingData(BaseModel):
    timestamp: float
    gazepoint_x: float
    gazepoint_y: float
    pupil_area_right_sq_mm: float
    pupil_area_left_sq_mm: float
    eye_event: str
    euclidean_distance: float
    prev_euclidean_distance: float

# Route to forward the request to the model API
@app.post("/classify")
async def classify(eye_tracking_data: EyeTrackingData):
    try:
        # Send the POST request to the model API
        response = requests.post(
            "http://localhost:8080/predict",
            json=eye_tracking_data.dict()
        )
        # Raise an exception if the request failed
        response.raise_for_status()
        # Return the model's response
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "Model Client Backend is running!"}
