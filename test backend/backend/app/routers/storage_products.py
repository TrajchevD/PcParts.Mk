from fastapi import APIRouter, HTTPException
from app.services.storage_products_service import (
    list_storage,
    get_storage_details,
)

router = APIRouter(prefix="/api/products/storage", tags=["Storage"])


@router.get("")
def get_storage(
    storage_type: str | None = None,
    min_capacity: int | None = None,
    sort: str = "price_asc",   # 👈 NEW
    limit: int = 24,
    offset: int = 0,
):
    filters = {
        "storage_type": storage_type,
        "min_capacity": min_capacity,
    }
    return list_storage(filters, sort, limit, offset)


@router.get("/{product_id}")
def get_storage_item(product_id: int):
    data = get_storage_details(product_id)
    if not data:
        raise HTTPException(404, "Storage not found")
    return data
