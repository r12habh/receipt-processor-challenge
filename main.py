# Import required modules
from fastapi import FastAPI, HTTPException, \
    Request  # FastAPI is used to create APIs quickly, and HTTPException handles errors.
from pydantic import ValidationError
import uuid  # Generates unique IDs for receipts.
import logging
from fastapi.responses import JSONResponse
from rate_limiter import RateLimiter
from time import time
from models import Receipt, PointsResponse, ReceiptResponse
from utils import calculate_points

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Rate limiting configuration (simple in-memory implementation)
rate_limiter = RateLimiter(max_requests=10)  # Customize as needed

# Create an instance of the FastAPI app
app = FastAPI(
    title="Receipt Processor API",
    description="A simple API for processing and calculating points for receipts",
    version="1.0.0",
    # openapi_url="/api/docs",
    # docs_url="/api/docs",
    # redoc_url="/api/redoc"  # ReDoc provides a user-friendly interface for API documentation.
)  # This initializes the FastAPI application where routes (endpoints) are defined.

# In-memory storage for receipts and their points
receipts_store = {}  # Dictionary to store receipt IDs and their corresponding points.


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware for logging requests and adding processing time
    :param request:
    :param call_next:
    :return:
    """
    logger.info(f"Request: {request.method} {request.url}")
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """
    Custom exception handler for validation errors
    :param request:
    :param exc:
    :return:
    """
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )


# Define an endpoint to process a receipt and calculate its points
@app.post("/receipts/process", response_model=ReceiptResponse)
async def process_receipt(request: Request, receipt: Receipt):
    # Apply rate limiting
    await rate_limiter.limit_request(request)

    try:
        # Generate a unique ID
        receipt_id = str(uuid.uuid4())

        # Calculate points
        points = calculate_points(receipt)

        # Store the receipt and its points
        receipts_store[receipt_id] = points

        logger.info(f"Receipt processed: {receipt_id}")
        return ReceiptResponse(id=receipt_id)

    except Exception as e:
        logger.error(f"Error processing receipt: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the receipt")


@app.get("/receipts/{uid}/points", response_model=PointsResponse)
async def get_points(uid: str):
    try:
        # Check if the receipt ID exists in the store
        if uid not in receipts_store:
            logger.warning(f"Receipt not found: {uid}")
            raise HTTPException(status_code=404, detail="Receipt not found")

        logger.info(f"Points retrieved for receipt: {uid}")
        # Return the points for the receipt
        return PointsResponse(points=receipts_store[uid])
    except Exception as e:
        logger.error(f"Error retrieving points: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the points")


@app.get("/health")
async def health_check():
    """
    Simple health check endpoint
    :return:
    """
    return {"status": "healthy"}

# Entry point for running the application
if __name__ == "__main__":
    import uvicorn  # Uvicorn is a server for running FastAPI applications.

    uvicorn.run(app, host="0.0.0.0", port=8000)  # Start the server on port 8000
