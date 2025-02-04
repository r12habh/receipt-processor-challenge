import math
from datetime import datetime
from models import Receipt
from typing import List


def rule8(items: List):
    points = 0
    for item in items:
        item_name = item.shortDescription.strip()
        if item_name[0].lower() == 'g':
            points += 10

    return points


def calculate_points(receipt: Receipt) -> int:
    """
    Calculates points for the given receipt based on several rules.

    Args:
        receipt (Receipt): The receipt object.

    Returns:
         int: The total points for the receipt.
    """
    points = 0

    # Rule 1: One point for every alphanumeric character in the retailer name
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
    # multiply the price by 0.2 and round up the nearest integer
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
    if datetime.strptime("14:01", "%H:%M").time() <= purchase_time < datetime.strptime("16:00", "%H:%M").time():
        points += 10

    points += rule8(receipt.items)

    return points


def generate_receipt_hash(receipt: Receipt) -> str:
    """
    Generates SHA-256 hash for the given receipt to detect duplicates.
    Normalizes the receipt data before hashing to ensure consistent results.

    Args:
        receipt (Receipt): The receipt object.

    Returns:
        str: The SHA-256 hash of the receipt.
    """
    import hashlib
    import json
    # Create a normalized dictionary of receipt data
    receipt_dict = {
        'retailer': receipt.retailer.strip().lower(),  # Normalize retailer name
        'purchaseDate': receipt.purchaseDate,
        'purchaseTime': receipt.purchaseTime,
        'items': [
            {
                'shortDescription': item.shortDescription.strip().lower(),
                'price': float(item.price)
            }
            for item in sorted(  # Sort items to ensure consistent ordering
                receipt.items,
                key=lambda x: (x.shortDescription.strip().lower(), float(x.price))
            )
        ],
        'total': float(receipt.total)  # Ensure consistent float representation
    }

    # Convert to JSON string with sorted keys for consistency
    receipt_json = json.dumps(receipt_dict, sort_keys=True)

    # Generate hash using SHA-256
    return hashlib.sha256(receipt_json.encode('utf8')).hexdigest()
