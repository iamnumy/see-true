from fastapi import FastAPI, HTTPException, UploadFile, File
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/classify")
async def upload_csv(file: UploadFile = File(...)):
    try:
        # Read the uploaded file using pandas
        df = pd.read_csv(file.file)
        df.columns = df.columns.str.strip()

        # Check for required columns
        required_columns = [
            "Timestamp", "Gazepoint X", "Gazepoint Y",
            "Pupil area (right) sq mm", "Pupil area (left) sq mm", "Eye event"
        ]
        if not all(column in df.columns for column in required_columns):
            raise HTTPException(status_code=400, detail="Missing required columns in the CSV file")

        predictions = []
        for index, row in df.iterrows():
            data = {
                "timestamp": row["Timestamp"],
                "gazepoint_x": row["Gazepoint X"],
                "gazepoint_y": row["Gazepoint Y"],
                "pupil_area_right_sq_mm": row["Pupil area (right) sq mm"],
                "pupil_area_left_sq_mm": row["Pupil area (left) sq mm"],
                "eye_event": row["Eye event"].strip()
            }

            try:
                response = requests.post(
                    "http://localhost:8080/predict",  # Use the existing /predict endpoint
                    json=data
                )
                response.raise_for_status()
                predictions.append(response.json())
            except requests.exceptions.RequestException as e:
                raise HTTPException(status_code=500, detail=f"Error while calling model API: {str(e)}")

        return {"message": "Predictions generated successfully", "predictions": predictions}

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="The uploaded CSV file is empty or invalid.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Model Client Backend is running!"}
