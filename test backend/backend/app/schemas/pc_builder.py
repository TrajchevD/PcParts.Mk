from pydantic import BaseModel
from typing import Optional, Literal, Dict, Any

Slot = Literal["cpu","mb","ram","gpu","storage"]

class BuildCreateIn(BaseModel):
    name: str = "My Build"

class BuildOut(BaseModel):
    build_id: int
    name: str
    parts: Dict[Slot, Optional[int]]  # slot -> product_id
    constraints: Dict[str, Any]

class SlotUpdateIn(BaseModel):
    product_id: Optional[int]  # allow clearing slot with null

# class OptionsIn(BaseModel):
#     slot: Slot
#     search: Optional[str] = None
#     filters: Dict[str, Any] = {}
#     selected: Dict[str, Optional[int]] = {}
#     limit: int = 20
#     offset: int = 0

class OptionsIn(BaseModel):
    build_id: int
    slot: str
    search: Optional[str] = None
    filters: Dict = {}
    sort: Optional[str] = "price_asc"   # ✅ ADD THIS
    limit: int = 20
    offset: int = 0


class OptionItem(BaseModel):
    product_id: int
    canonical_title: str
    best_price: Optional[float] = None
    store: Optional[str] = None
    # plus specs fields depending on slot:
    specs: Dict[str, Any] = {}
