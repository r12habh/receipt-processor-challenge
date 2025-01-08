from datetime import datetime
from typing import List
from db import TagDB, ReceiptDB
from sqlalchemy.orm import Session


def determine_tags(receipt: ReceiptDB) -> List[str]:
    """
    Determine which tags should be applied to a receipt based on predefined conditions.
    :param receipt:
    :return tags:
    """
    tags = []

    # Check for Loyal Customer tag
    if sum(c.isalnum() for c in receipt.retailer) > 10:
        tags.append("Loyal Customer")

    # Check for Big Spender tag
    if receipt.total > 100:
        tags.append("Big Spender")

    # Check for Weekend Shopper tag
    purchase_date = datetime.strptime(receipt.purchase_date, "%Y-%m-%d")
    if purchase_date.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
        tags.append("Weekend Shopper")

    return tags


def get_or_create_tag(db: Session, tag_name: str) -> TagDB:
    """
    Get existing tag or create a new tag in the database if it doesn't exist.
    :param db:
    :param tag_name:
    :return:
    """
    tag = db.query(TagDB).filter(TagDB.name == tag_name).first()

    if not tag:
        tag = TagDB(name=tag_name)
        db.add(tag)
        db.commit()
        db.refresh(tag)

    return tag


def tag_receipt(db: Session, receipt_id: str) -> List[str]:
    """
    Apply appropriate tags to a receipt based on conditions.
    Returns list of applied tag names.
    :param db:
    :param receipt_id:
    :return:
    """
    receipt = db.query(ReceiptDB).filter(ReceiptDB.id == receipt_id).first()
    if not receipt:
        raise ValueError(f"No receipt found with ID {receipt_id}")

    # Clear existing tags
    receipt.tags = []

    # Determine and apply new tags
    tag_names = determine_tags(receipt)

    for tag_name in tag_names:
        tag = get_or_create_tag(db, tag_name)
        receipt.tags.append(tag)

    db.commit()

    return tag_names
