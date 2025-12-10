from pydantic import BaseModel
from typing import Optional


class Customer(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    phone: str