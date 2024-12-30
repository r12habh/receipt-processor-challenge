# Import required modules
from fastapi import FastAPI, \
    Request  # FastAPI is used to create APIs quickly, and HTTPException handles errors.
from pydantic import ValidationError
import logging
from fastapi.responses import JSONResponse
from time import time
from api.routes import router
from db import init_db

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Create an instance of the FastAPI app
app = FastAPI(
    title="Receipt Processor API",
    description="A simple API for processing and calculating points for receipts",
    version="1.0.0",
    # openapi_url="/api/docs",
    # docs_url="/api/docs",
    # redoc_url="/api/redoc"  # ReDoc provides a user-friendly interface for API documentation.
)  # This initializes the FastAPI application where routes (endpoints) are defined.


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

# Include router
app.include_router(router)

# Entry point for running the application
if __name__ == "__main__":
    import uvicorn  # Uvicorn is a server for running FastAPI applications.

    uvicorn.run(app, host="0.0.0.0", port=8000)  # Start the server on port 8000
