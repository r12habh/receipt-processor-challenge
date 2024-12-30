from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import hashlib
import json
import os

Base = declarative_base()
DATABASE_URL = "sqlite:///data/receipts.db"


class ReceiptDB(Base):
    __tablename__ = 'receipts'

    id = Column(String(36), primary_key=True)
    retailer = Column(String(255), nullable=False)
    purchase_date = Column(String(10), nullable=False)
    purchase_time = Column(String(5), nullable=False)
    total = Column(Float, nullable=False)
    items = relationship('ItemDB', back_populates='receipt', cascade="all, delete-orphan")
    points = Column(Integer, nullable=False)
    receipt_hash = Column(String(64), nullable=False, unique=True)

    __table_args__ = (Index('idx_receipt_hash', 'receipt_hash'),)


class ItemDB(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    receipt_id = Column(String(36), ForeignKey('receipts.id', ondelete='CASCADE'), nullable=False)
    short_description = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    receipt = relationship('ReceiptDB', back_populates='items')


def init_db():
    # Create a 'data' directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')

    # Connect to the SQLite database
    engine = create_engine(DATABASE_URL)

    # Create all tables
    Base.metadata.create_all(engine)

    return sessionmaker(bind=engine)


# Database session management
SessionLocal = init_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
