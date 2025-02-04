from pydantic import BaseModel, field_validator, ValidationError
from typing import List
from datetime import datetime
from fastapi import HTTPException


class Item(BaseModel):
    """Model representing an individual item in a receipt."""
    shortDescription: str
    price: float


class Tag(BaseModel):
    """Model representing a receipt tag."""
    name: str


class Receipt(BaseModel):
    """Model representing a complete receipt."""
    retailer: str
    purchaseDate: str
    purchaseTime: str
    items: List[Item]
    total: float

    @field_validator('purchaseDate')
    def validate_purchase_date(cls, v):
        """Validate the purchase date format."""
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    @field_validator('purchaseTime')
    def validate_purchase_time(cls, v):
        """Validate the purchase time format."""
        try:
            datetime.strptime(v, '%H:%M')
            return v
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")

    @field_validator('retailer')
    def validate_retailer(cls, v):
        """Ensure retailer name is not empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Retailer name cannot be empty")
        return v

    @field_validator('items')
    def validate_items(cls, v):
        """Ensure at least one item is present in the receipt."""
        if not v or len(v) == 0:
            raise ValueError("Receipt must have at least one item")
        return v

    @field_validator('total')
    def validate_total(cls, v, info):
        """Validate that total matches sum of item prices"""
        try:
            items = info.data.get('items', [])
            if items:
                items_total = sum(item.price for item in items)
                if abs(items_total - v) > 0.01:  # Allow for small point differences
                    raise ValueError("Total does not match sum of item prices")
        except Exception as e:
            raise ValueError(f"Error validating total: {e}")
        return v


class ReceiptResponse(BaseModel):
    """Response model to return the receipt ID."""
    id: str  # The unique ID of the receipt.


class PointsResponse(BaseModel):
    """Response model to return points for a receipt."""
    points: int  # The total points for a given receipt.


class TagResponse(BaseModel):
    """Response model for receipt tags."""
    receipt_id: str  # The ID of the receipt
    tags: List[str]  # The list of tags
