from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Lot(Base):
    __tablename__ = "lots"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    start_price = Column(Float, default=0.0)
    current = Column(Float, default=0.0)
    status = Column(String, default="running")
    created_at = Column(DateTime, default=datetime.utcnow)

    bids = relationship("Bid", back_populates="lot")

class Bid(Base):
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, index=True)
    lot_id = Column(Integer, ForeignKey("lots.id"))
    bidder_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    lot = relationship("Lot", back_populates="bids")