import pytest
from fastapi.testclient import TestClient
from main import app
from db import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///data/test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create a fixture for the test client
@pytest.fixture(scope="function")
def test_client():
    # Set up the database
    Base.metadata.create_all(bind=engine)

    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    # Create a test client
    client = TestClient(app)

    # Provide the client to the test
    yield client

    # Clean up
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def test_tag_receipt_loyal_customer(test_client):
    # Create a receipt with a long retailer name
    receipt_data = {
        "retailer": "SuperMegaMartExtra",
        "purchaseDate": "2024-01-01",
        "purchaseTime": "13:01",
        "total": 50.00,
        "items": [{"shortDescription": "Item 1", "price": 50.00}]
    }

    # Create receipt
    response = test_client.post("/receipts/process", json=receipt_data)
    assert response.status_code == 200
    receipt_id = response.json()["id"]

    # Tag the receipt as loyal customer
    response = test_client.post(f"/receipts/{receipt_id}/tags")
    assert response.status_code == 200

    # Verify tags
    tags = response.json()["tags"]
    assert "Loyal Customer" in tags
    assert len(tags) == 1


def test_tag_receipt_big_spender(test_client):
    # Create a receipt with total > $100
    receipt_data = {
        "retailer": "Store",
        "purchaseDate": "2024-01-01",
        "purchaseTime": "13:01",
        "total": 150.00,
        "items": [{"shortDescription": "Item 1", "price": 150.00}]
    }

    response = test_client.post("/receipts/process", json=receipt_data)
    assert response.status_code == 200
    receipt_id = response.json()["id"]

    # Tag the receipt
    response = test_client.post(f"/receipts/{receipt_id}/tags")
    assert response.status_code == 200

    # Verify tags
    tags = response.json()["tags"]
    assert "Big Spender" in tags


def test_tag_receipt_weekend_shopper(test_client):
    # Create a receipt with a weekend date
    receipt_data = {
        "retailer": "Store",
        "purchaseDate": "2024-01-06",  # This is a Saturday
        "purchaseTime": "13:01",
        "total": 50.00,
        "items": [{"shortDescription": "Item 1", "price": 50.00}]
    }

    response = test_client.post("/receipts/process", json=receipt_data)
    assert response.status_code == 200
    receipt_id = response.json()["id"]

    # Tag the receipt
    response = test_client.post(f"/receipts/{receipt_id}/tags")
    assert response.status_code == 200

    # Verify tags
    tags = response.json()["tags"]
    assert "Weekend Shopper" in tags


def test_tag_receipt_multiple_tags(test_client):
    # Create a receipt that should get multiple tags
    receipt_data = {
        "retailer": "SuperMegaMartExtra",
        "purchaseDate": "2024-01-06",  # Saturday
        "purchaseTime": "13:01",
        "total": 150.00,
        "items": [{"shortDescription": "Item 1", "price": 150.00}]
    }

    response = test_client.post("/receipts/process", json=receipt_data)
    assert response.status_code == 200
    receipt_id = response.json()["id"]

    # Tag the receipt
    response = test_client.post(f"/receipts/{receipt_id}/tags")
    assert response.status_code == 200

    # Verify all applicable tags are present
    tags = response.json()["tags"]
    assert "Loyal Customer" in tags
    assert "Big Spender" in tags
    assert "Weekend Shopper" in tags
    assert len(tags) == 3


def test_tag_nonexistent_receipt(test_client):
    response = test_client.post("/receipts/nonexistent-id/tags")
    assert response.status_code == 404
