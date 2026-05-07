from pydantic import BaseModel
from typing import Optional

class ProductOut(BaseModel):
    id: int
    store: str
    category: str
    title: str
    link: str
    price: str
    price_text: str
    image: Optional[str] = None
    in_stock: int
    last_seen_at: str
    created_at: str
    updated_at: str

class CategoryOut(BaseModel):
    category: str
    count: int
