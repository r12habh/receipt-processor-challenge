from fastapi.testclient import TestClient
from main import app, calculate_points, Receipt
from datetime import datetime
import math

# Create the test client
client = TestClient(app)


def test_target_receipt():
    receipt = {
        "retailer": "Target",
        "purchaseDate": "2022-01-01",
        "purchaseTime": "13:01",
        "items": [
            {
                "shortDescription": "Mountain Dew 12PK",
                "price": "6.49"
            },
            {
                "shortDescription": "Emils Cheese Pizza",
                "price": "12.25"
            },
            {
                "shortDescription": "Knorr Creamy Chicken",
                "price": "1.26"
            },
            {
                "shortDescription": "Doritos Nacho Cheese",
                "price": "3.35"
            },
            {
                "shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ",
                "price": "12.00"
            }
        ],
        "total": "35.35"
    }

    # Print detailed breakdown for debugging
    receipt_obj = Receipt(**receipt)
    points = calculate_points(receipt_obj)
    print(f"Target Receipt Points Breakdown:")
    print(f"Retailer Chars: {sum(c.isalnum() for c in receipt_obj.retailer)}")
    print(f"Items Points: {(len(receipt_obj.items) // 2) * 5}")
    print(
        f"Special Item Points: {sum(math.ceil(float(item.price) * 0.2) for item in receipt_obj.items if len(item.shortDescription) % 3 == 0)}")
    print(f"Day Points: {6 if datetime.strptime(receipt_obj.purchaseDate, '%Y-%m-%d').day % 2 == 1 else 0}")
    print(
        f"Time Points: {10 if (datetime.strptime('14:00', '%H:%M').time() <= datetime.strptime(receipt_obj.purchaseTime, '%H:%M').time() <= datetime.strptime('16:00', '%H:%M').time()) else 0}")

    assert points == 28, f"Expected 28 points but got {points}"


def test_market_receipt():
    receipt = {
        "retailer": "M&M Corner Market",
        "purchaseDate": "2022-03-20",
        "purchaseTime": "14:33",
        "items": [
            {
                "shortDescription": "Gatorade",
                "price": "2.25"
            },
            {
                "shortDescription": "Gatorade",
                "price": "2.25"
            },
            {
                "shortDescription": "Gatorade",
                "price": "2.25"
            },
            {
                "shortDescription": "Gatorade",
                "price": "2.25"
            }
        ],
        "total": "9.00"
    }

    # Print detailed breakdown for debugging
    receipt_obj = Receipt(**receipt)
    points = calculate_points(receipt_obj)
    print(f"Market Receipt Points Breakdown:")
    print(f"Retailer Chars: {sum(c.isalnum() for c in receipt_obj.retailer)}")
    print(f"Total Round Points: {50 if float(receipt_obj.total).is_integer() else 0}")
    print(f"Total 0.25 Multiple Points: {25 if float(receipt_obj.total) % 0.25 == 0 else 0}")
    print(f"Items Points: {(len(receipt_obj.items) // 2) * 5}")
    print(
        f"Time Points: {10 if (datetime.strptime('14:00', '%H:%M').time() <= datetime.strptime(receipt_obj.purchaseTime, '%H:%M').time() <= datetime.strptime('16:00', '%H:%M').time()) else 0}")

    assert points == 109, f"Expected 109 points but got {points}"


def test_process_receipt():
    receipt = {
        "retailer": "Target",
        "purchaseDate": "2022-01-01",
        "purchaseTime": "13:01",
        "items": [
            {
                "shortDescription": "Mountain Dew 12PK",
                "price": "6.49"
            }
        ],
        "total": "6.49"
    }

    # Test the process receipt endpoint
    response = client.post("/receipts/process", json=receipt)
    assert response.status_code == 200, f"Expected 200 status code, got {response.status_code}"
    assert "id" in response.json()
    receipt_id = response.json()["id"]

    # Test get points endpoint
    points_response = client.get(f"/receipts/{receipt_id}/points")
    assert points_response.status_code == 200
    assert "points" in points_response.json()
