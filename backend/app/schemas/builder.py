from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field

Slot = Literal["cpu", "gpu", "mb", "ram", "storage"]
VALID_SLOTS: set[str] = {"cpu", "gpu", "mb", "ram", "storage"}


class BuildCreateIn(BaseModel):
    name: str = "My Build"


class BuildRenameIn(BaseModel):
    name: str


class SlotUpdateIn(BaseModel):
    product_id: Optional[int] = None  # None = clear the slot


class OptionsIn(BaseModel):
    build_id: int
    slot: Slot
    search: Optional[str] = None
    filters: Dict[str, Any] = {}
    sort: str = "price_asc"
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)
