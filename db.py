from sqlalchemy import create_engine, Column, Integer, String, Float, Table, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()
DATABASE_URL = "sqlite:///data/receipts.db"

# Association table for receipt-tag many-to-many associations
receipt_tags = Table(
    'receipt_tags',
    Base.metadata,
    Column('receipt_id', String(36), ForeignKey('receipts.id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE')),
    Index('idx_receipt_tag', 'receipt_id', 'tag_id')
)


class ReceiptDB(Base):
    __tablename__ = 'receipts'

    id = Column(String(36), primary_key=True)
    retailer = Column(String(255), nullable=False)
    purchase_date = Column(String(10), nullable=False)
    purchase_time = Column(String(5), nullable=False)
    total = Column(Float, nullable=False)
    items = relationship('ItemDB', back_populates='receipt', cascade="all, delete-orphan",
                         lazy='joined')  # Enabled joined loading by default
    points = Column(Integer, nullable=False)
    receipt_hash = Column(String(64), nullable=False, unique=True)
    tags = relationship('TagDB', secondary=receipt_tags, back_populates='receipts')

    # Add composite index for date-based queries
    __table_args__ = (
        Index('idx_receipt_hash', 'receipt_hash'),
        Index('idx_purchase_date_retailer', 'purchase_date', 'retailer'),
    )

    @property
    def purchase_datetime(self):
        """
        Helper property to get datetime object when needed
        :return:
        """
        return datetime.strptime(f'{self.purchase_date} {self.purchase_time}', '%Y-%m-%d %H:%M')


class TagDB(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    receipts = relationship('ReceiptDB', secondary=receipt_tags, back_populates='tags')


class ItemDB(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    receipt_id = Column(String(36), ForeignKey('receipts.id', ondelete='CASCADE'), nullable=False)
    short_description = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    receipt = relationship('ReceiptDB', back_populates='items')

    __table_args__ = (
        Index('idx_receipt_items', 'receipt_id', 'short_description'),
    )


def init_db():
    # Create a 'data' directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')

    # Connect to the SQLite database
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10
    )

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
