from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class BidBase(BaseModel):
    bidder_name: str
    amount: float

class BidCreate(BidBase):
    pass

class BidResponse(BidBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class LotBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_price: float

class LotCreate(LotBase):
    pass

class LotResponse(LotBase):
    id: int
    current: float
    status: str
    class Config:
        from_attributes = True