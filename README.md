# SeeTrue Backend Project

This project sets up a backend for interacting with the SeeTrue classification model using FastAPI and Docker. The backend acts as an interface for sending data to the model API and receiving predictions.


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


API Endpoints
/classify (POST)

    Description: Upload a CSV file to classify data and get predictions from the model API.
    Request Body: form-data
        Key: file
        Value: [Select your CSV file] (File)

/ (GET)

    Description: Health check endpoint to confirm the service is running.
    Response: { "message": "Model Client Backend is running!" }
