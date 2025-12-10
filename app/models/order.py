from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class OrderItem(BaseModel):
    product_id: int
    quantity: int


class Order(BaseModel):
    id: Optional[int] = None
    customer_id: int
    items: List[OrderItem]
    total_price: Optional[float] = None
    created_at: Optional[datetime] = None
    status: str = "pending"