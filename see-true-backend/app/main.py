import pandas as pd
import asyncio
import os
import requests
import traceback
import logging
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, UploadFile, File, status
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from data_cleaner import clean_data  # Import the cleaning function

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Directory for temporary file storage
TEMP_DIR = "uploaded_files"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Global results store
results_store: Dict[str, Any] = {}

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Adjust frontend URL if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DataBatches(BaseModel):
    timestamp: List[float]
    gazepoint_x: List[float]
    gazepoint_y: List[float]
    pupil_area_right_sq_mm: List[float]
    pupil_area_left_sq_mm: List[float]
    eye_event: List[str]

@app.post("/classify_in_batches")
async def classify_in_batches(file: UploadFile = File(...), batch_size: int = 500):
    """
    Handle file upload and initiate batch processing.
    """
    try:
        # Save the file temporarily
        file_path = os.path.join(TEMP_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Generate a unique key for the request
        results_key = str(hash(file.filename))
        results_store[results_key] = {"status": "processing", "final_result": {}}

        logger.info(f"File '{file.filename}' uploaded successfully. Processing started with key: {results_key}")

        # Process the file in the background
        asyncio.create_task(process_file_in_batches(file_path, results_key, batch_size))

        return {"message": "Processing started. Retrieve results using the key.", "key": results_key}

    except Exception as e:
        logger.error(f"Error during file upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")



async def process_file_in_batches(file_path: str, key: str, batch_size: int = 500):
    """
    Process the uploaded file in batches after cleaning and aggregate the results.
    Skips normalization since the model already provides normalized probabilities.
    """
    try:
        # Step 1: Clean the data using the cleaning function
        logger.info(f"Starting data cleaning for file: {file_path}")
        cleaned_df = clean_data(file_path)
        logger.info(f"Data cleaned successfully. Columns: {cleaned_df.columns.tolist()}")

        # Define the path for the cleaned CSV
        cleaned_file_path = os.path.join(TEMP_DIR, f"cleaned_{file_path.split('/')[-1]}")

        # Save the cleaned data to a CSV file
        cleaned_df.to_csv(cleaned_file_path, index=False)
        logger.info(f"Cleaned data saved to {cleaned_file_path}")

        # Initialize aggregated results
        aggregated_results = {"walking": 0.0, "playing": 0.0, "reading": 0.0, "process_data": 0}

        # Split the DataFrame into batches
        total_rows = len(cleaned_df)
        logger.info(f"Processing {total_rows} rows in cleaned file: {file_path}")

        def validate_payload(payload):
            required_keys = ["timestamp", "gazepoint_x", "gazepoint_y", "pupil_area_right_sq_mm", "pupil_area_left_sq_mm", "eye_event"]
            for key in required_keys:
                if key not in payload or not payload[key]:
                    raise ValueError(f"Missing or empty key: {key}")

        for start_row in range(0, total_rows, batch_size):
            # Extract the batch
            chunk_df = cleaned_df.iloc[start_row:start_row + batch_size]

            # Prepare the payload for the model API
            data = {
                "timestamp": chunk_df["timestamp"].tolist(),
                "gazepoint_x": chunk_df["gazepoint_x"].tolist(),
                "gazepoint_y": chunk_df["gazepoint_y"].tolist(),
                "pupil_area_right_sq_mm": chunk_df["pupil_area_right_sq_mm"].tolist(),
                "pupil_area_left_sq_mm": chunk_df["pupil_area_left_sq_mm"].tolist(),
                "eye_event": chunk_df["eye_event"].astype(str).tolist(),
            }

            # Validate and log payload
            validate_payload(data)
            # logger.info(f"Payload sent to model: {data}")

            try:
                # Send batch to prediction API
                response = requests.post("http://localhost:8080/predict", json=data)
                response.raise_for_status()
                batch_result = response.json()

                # Log batch result
                # logger.info(f"Batch result: {batch_result}")

                # Aggregating the results directly without normalization
                aggregated_results["walking"] += batch_result["walking"] * batch_result["process_data"]
                aggregated_results["playing"] += batch_result["playing"] * batch_result["process_data"]
                aggregated_results["reading"] += batch_result["reading"] * batch_result["process_data"]
                aggregated_results["process_data"] += batch_result["process_data"]

            except requests.exceptions.RequestException as e:
                logger.error(f"Error during API request: {e}")
                continue

        # When all batches are processed, aggregate results directly
        if aggregated_results["process_data"] > 0:
            aggregated_results["walking"] /= aggregated_results["process_data"]
            aggregated_results["playing"] /= aggregated_results["process_data"]
            aggregated_results["reading"] /= aggregated_results["process_data"]

        # Final aggregation to ensure the total probability sums to 1
        total_sum = (
            aggregated_results["walking"]
            + aggregated_results["playing"]
            + aggregated_results["reading"]
        )
        if total_sum > 0:
            aggregated_results["walking"] /= total_sum
            aggregated_results["playing"] /= total_sum
            aggregated_results["reading"] /= total_sum

        # Log final results
        logger.info(f"Final aggregated results: {aggregated_results}")

        # Update the results store
        results_store[key] = {"status": "complete", "final_result": aggregated_results}

    except Exception as e:
        logger.error(f"Error during batch processing: {str(e)}")
        results_store[key] = {"status": "error", "error": str(e)}

    finally:
        # Clean up the original uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)


@app.get("/results/{key}")
async def get_results(key: str):
    """
    Retrieve processing results for a specific key.
    """
    if key not in results_store:
        raise HTTPException(status_code=404, detail="Results not found.")

    result = results_store[key]

    # Check if processing is complete and return the final result
    if result["status"] == "complete":
        final_result = result["final_result"]

        # Determine the final activity based on the highest probability between walking, playing, and reading
        final_activity = max(
            [("walking", final_result["walking"]),
             ("playing", final_result["playing"]),
             ("reading", final_result["reading"])],
            key=lambda x: x[1]
        )[0]  # Extract the activity name with the highest score

        final_activity_response = {
            "walking": final_result["walking"],
            "playing": final_result["playing"],
            "reading": final_result["reading"],
            "final_activity": final_activity  # Now correctly showing walking, playing, or reading
        }

        return {"status": "complete", "final_result": final_activity_response}

    # If processing is not complete yet, send the current status
    return {"status": result["status"], "final_result": {}}



@app.get("/")
def root():
    """
    Health check endpoint.
    """
    return {"message": "Batch Processing API is running!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, workers=1, access_log=True)
