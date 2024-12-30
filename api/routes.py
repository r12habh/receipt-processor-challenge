# Import required modules
from fastapi import APIRouter, Depends, HTTPException, \
    Request  # HTTPException handles errors.
import uuid  # Generates unique IDs for receipts.
import logging
from rate_limiter import RateLimiter
from models import Receipt, PointsResponse, ReceiptResponse
from utils import calculate_points, generate_receipt_hash
from db import get_db, ReceiptDB, ItemDB
from typing import Annotated
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Rate limiting configuration (simple in-memory implementation)
rate_limiter = RateLimiter(max_requests=10)  # Customize as needed

# In-memory storage for receipts and their points
receipts_store = {}  # Dictionary to store receipt IDs and their corresponding points.

receipts_hash = {}  # Dictionary to store receipt hashes and their corresponding IDs.

# Create router instance
router = APIRouter()


# Define an endpoint to process a receipt and calculate its points
@router.post("/receipts/process", response_model=ReceiptResponse)
async def process_receipt(request: Request, receipt: Receipt, db=Depends(get_db)):
    # Apply rate limiting
    await rate_limiter.limit_request(request)

    try:
        # Generate hash for duplicate detection
        receipt_hash = generate_receipt_hash(receipt)

        # Check if the receipt hash already exists in the store
        existing_receipt = db.query(ReceiptDB).filter(
            ReceiptDB.receipt_hash == receipt_hash
        ).first()

        if existing_receipt:
            logger.info(f"Duplicate receipt detected: {existing_receipt.id}")
            # raise HTTPException(status_code=409, detail="Duplicate receipt detected")
            # Return the existing receipt ID if it exists
            return ReceiptResponse(id=existing_receipt.id)

        # Generate a unique ID
        receipt_id = str(uuid.uuid4())

        # Calculate points
        points = calculate_points(receipt)

        # Create database receipt object
        db_receipt = ReceiptDB(
            id=receipt_id,
            retailer=receipt.retailer,
            purchase_date=receipt.purchaseDate,
            purchase_time=receipt.purchaseTime,
            total=receipt.total,
            points=points,
            receipt_hash=receipt_hash,
        )

        # Add items
        for item in receipt.items:
            db_receipt.items.append(
                ItemDB(
                    short_description=item.shortDescription,
                    price=item.price,
                )
            )

        db.add(db_receipt)
        db.commit()

        # Store the receipt and its points
        receipts_store[receipt_id] = points

        # Store the receipt hash and its corresponding ID
        receipts_hash[receipt_hash] = receipt_id

        # Return the receipt ID
        logger.info(f"Receipt stored: {receipt_id}")
        return ReceiptResponse(id=receipt_id)

    except Exception as e:
        logger.error(f"Error processing receipt: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the receipt")


@router.get("/receipts/{uid}/points", response_model=PointsResponse)
async def get_points(uid: str, db=Depends(get_db)):
    try:
        receipt = db.query(ReceiptDB).filter(ReceiptDB.id == uid).first()

        if not receipt:
            logger.info(f"Receipt not found: {uid}")
            raise HTTPException(status_code=404, detail="Receipt not found")

        logger.info(f"Points retrieved for receipt: {uid}")
        return PointsResponse(points=receipt.points)
    except Exception as e:
        logger.error(f"Error retrieving points: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the points")


@router.get("/health")
async def health_check():
    """
    Simple health check endpoint
    :return:
    """
    return {"status": "healthy"}
