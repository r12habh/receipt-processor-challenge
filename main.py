from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import List
import uuid
from datetime import datetime
import math

app = FastAPI()

# In-memory storage for receipts and their points
receipts_store = {}


class Item(BaseModel):
    shortDescription: str
    price: float

    @field_validator('price')
    def validate_price(cls, v):
        try:
            float(v)
            return v
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid price format")


class Receipt(BaseModel):
    retailer: str
    purchaseDate: str
    purchaseTime: str
    items: List[Item]
    total: str

    @field_validator('purchaseDate')
    def validate_purchase_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    @field_validator('purchaseTime')
    def validate_purchase_time(cls, v):
        try:
            datetime.strptime(v, '%H:%M')
            return v
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")


class ReceiptResponse(BaseModel):
    id: str


class PointsResponse(BaseModel):
    points: int


def calculate_points(receipt: Receipt) -> int:
    """
        Calculates points for the given receipt based on several rules.

        Args:
            receipt (Receipt): The receipt object.

        Returns:
            int: The total points for the receipt.
    """
    points = 0

    # Rule 1: One point for every alphanumeric character n the retailer name
    points += sum(c.isalnum() for c in receipt.retailer)

    # Rule 2: 50 points if the total is a round dollar amount with no cents
    total = float(receipt.total)
    if total.is_integer():
        points += 50

    # Rule 3: 25 points if the total is a multiple of 0.25
    if total % 0.25 == 0:
        points += 25

    # Rule 4: 5 points for every two items on the receipt
    points += (len(receipt.items) // 2) * 5

    # Rule 5: If the trimmed length of the item description is a multiple of 3,
    # multiply the price by 0.2 and round up to the nearest integer
    for item in receipt.items:
        desc_length = len(item.shortDescription.strip())
        if desc_length % 3 == 0:
            item_points = math.ceil(float(item.price) * 0.2)
            points += item_points

    # Rule 6: 6 points if the day in the purchase date is odd
    purchase_date = datetime.strptime(receipt.purchaseDate, "%Y-%m-%d")
    if purchase_date.day % 2 == 1:
        points += 6

    # Rule 7: 10 points if the time of purchase is after 2:00pm and before 4:00pm
    purchase_time = datetime.strptime(receipt.purchaseTime, "%H:%M").time()
    if datetime.strptime("14:00", "%H:%M").time() <= purchase_time <= datetime.strptime("16:00", "%H:%M").time():
        points += 10

    return points


@app.post("/receipts/process", response_model=ReceiptResponse)
async def process_receipt(receipt: Receipt):
    # Generate a unique ID
    receipt_id = str(uuid.uuid4())

    # Calculate points
    points = calculate_points(receipt)

    # Store the receipt and its points
    receipts_store[receipt_id] = points

    return ReceiptResponse(id=receipt_id)


@app.get("/receipts/{uid}/points", response_model=PointsResponse)
async def get_points(uid: str):
    if uid not in receipts_store:
        raise HTTPException(status_code=404, detail="Receipt not found")

    return PointsResponse(points=receipts_store[uid])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
