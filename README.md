# SeeTrue Backend Project

This project sets up a backend for interacting with the SeeTrue classification model using FastAPI and Docker. The backend acts as an interface for sending data to the model API and receiving predictions.

## Project Structure

SeeTrue-backend/ │ ├── app/ │ ├── main.py # FastAPI application │ ├── Dockerfile # Dockerfile to containerize the backend │ ├── requirements.txt # Python dependencies │ └── docker-compose.yml # Docker Compose file for orchestrating containers



## Prerequisites
- **Python 3.7+** installed on your system.
- **Docker and Docker Compose** installed.
- A running instance of your SeeTrue model on `localhost:8080`.

## Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/iamnumy/see-true
cd SeeTrue-backend
python -m venv venv
cd app
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000


POST /classify
{
  "timestamp": 123456789.0,
  "gazepoint_x": 0.5,
  "gazepoint_y": 0.5,
  "pupil_area_right_sq_mm": 12.34,
  "pupil_area_left_sq_mm": 11.22,
  "eye_event": "FB",
  "euclidean_distance": 1.5,
  "prev_euclidean_distance": 1.5
}
