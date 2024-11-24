import pandas as pd
import asyncio
import os
import requests
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for processing results
results_store: Dict[str, Any] = {}

# Directory for temporary file storage
TEMP_DIR = "uploaded_files"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Replace with your actual model's prediction endpoint
MODEL_API_URL = "http://localhost:8080/predict"


@app.post("/classify_in_batches")
async def classify_in_batches(file: UploadFile = File(...)):
    """
    Handle file upload, save it temporarily, and start background processing.
    """
    try:
        # Save the file locally for processing
        file_path = os.path.join(TEMP_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Generate a unique key for the request
        results_key = str(hash(file.filename))
        results_store[results_key] = {"batches": [], "status": "processing"}

        # Process the file in the background
        asyncio.create_task(process_file(file_path, results_key))

        return {"message": "Processing started. Retrieve results using the key.", "key": results_key}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


async def process_file(file_path: str, key: str):
    """
    Process the file in batches and store results incrementally.
    """
    try:
        # Load the CSV file
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip().str.lower()  # Normalize column names

        # Column mapping and validation
        column_mapping = {
            "timestamp": "timestamp",
            "gazepoint x": "gazepoint_x",
            "gazepoint y": "gazepoint_y",
            "pupil area (right) sq mm": "pupil_area_right_sq_mm",
            "pupil area (left) sq mm": "pupil_area_left_sq_mm",
            "eye event": "eye_event",
        }
        df.rename(columns=column_mapping, inplace=True)
        required_columns = list(column_mapping.values())

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise Exception(f"Missing required columns: {missing_columns}. Found: {df.columns.tolist()}")

        # Process the file in batches
        batch_size = 100
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i : i + batch_size]
            batch_results = []

            for _, row in batch.iterrows():
                data = {
                    "timestamp": row["timestamp"],
                    "gazepoint_x": row["gazepoint_x"],
                    "gazepoint_y": row["gazepoint_y"],
                    "pupil_area_right_sq_mm": row["pupil_area_right_sq_mm"],
                    "pupil_area_left_sq_mm": row["pupil_area_left_sq_mm"],
                    "eye_event": row["eye_event"],
                    "prev_euclidean_distance": results_store[key].get("prev_euclidean_distance", None),
                }

                # Call the model API to get predictions
                try:
                    response = requests.post(MODEL_API_URL, json=data)
                    response.raise_for_status()
                    model_response = response.json()
                    results_store[key]["prev_euclidean_distance"] = model_response["prev_euclidean_distance"]
                except requests.exceptions.RequestException as e:
                    model_response = {
                        "predictions": [],
                        "label_classes": [],
                        "prev_euclidean_distance": None,
                        "error": str(e),
                    }

                batch_results.append(model_response)

            # Store the batch results incrementally
            results_store[key]["batches"].append(batch_results)

            # Simulate delay for processing each batch
            await asyncio.sleep(1)  # Adjust as needed for realistic delay

        # Mark processing as complete
        results_store[key]["status"] = "complete"

    except Exception as e:
        results_store[key]["status"] = "error"
        results_store[key]["error"] = str(e)

    finally:
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)


@app.get("/results/{key}")
async def get_results(key: str):
    """
    Retrieve the current processing results for the given key.
    """
    if key not in results_store:
        raise HTTPException(status_code=404, detail="Results not found.")

    return results_store[key]


@app.get("/")
def root():
    """
    Health check endpoint.
    """
    return {"message": "Batch Processing API is running!"}
