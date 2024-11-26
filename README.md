# Receipt Processor

## Overview
This is a FastAPI-based web service for processing receipts and calculating points based on specific rules.

## Prerequisites
- Python 3.10+
- Docker (optional)
- Postman (recommended for API testing)

## Local Development Setup

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
uvicorn main:app --reload
```

### Run Tests
```bash
pytest test_receipt.py -v -s
```

## Docker Deployment

### Build Docker Image
```bash
docker build -t receipt-processor .
```

### Run Docker Container
```bash
docker run -p 8000:8000 receipt-processor
```

## API Testing with Postman

### Import Postman Collection
1. Open Postman
2. Click "Import" 
3. Select the `postman-requests.json` file
4. The collection with sample requests will be imported

### Sample Requests Included
- Process Target Receipt
- Get Points for Target Receipt
- Process M&M Market Receipt
- Get Points for M&M Market Receipt

### Using the Postman Collection
1. Start the application locally or in Docker
2. Open the imported Postman collection
3. For "Get Points" requests, replace `{{receipt_id}}` with the ID received from the corresponding "Process Receipt" request

## API Endpoints

### Process Receipt
- **POST** `/receipts/process`
  - Processes a receipt and returns a unique receipt ID
  - Request Body: Receipt JSON object

### Get Points
- **GET** `/receipts/{id}/points`
  - Retrieves points for a processed receipt
  - Requires a valid receipt ID from the process endpoint

## Point Calculation Rules
1. One point for every alphanumeric character in retailer name
2. 50 points for round dollar totals
3. 25 points for totals that are multiples of 0.25
4. 5 points for every two items
5. Special item points based on description length
6. 6 points for purchases on odd days
7. 10 points for purchases between 2-4 PM

## Project Structure
```
receipt-processor/
│
├── main.py                # FastAPI application
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── test_main.py            # Pytest test file
├── README.md               # Project documentation
└── postman-requests.json   # Postman API collection
```
