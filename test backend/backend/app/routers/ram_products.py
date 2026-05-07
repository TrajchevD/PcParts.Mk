from fastapi import APIRouter, HTTPException
from app.services.ram_products_service import (
    list_rams,
    get_ram_details,
)

router = APIRouter(prefix="/api/products/ram", tags=["RAM"])

@router.get("")
def get_rams(
    memory_type: str | None = None,
    min_capacity: int | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    limit: int = 24,
    offset: int = 0,
):
    filters = {
        "memory_type": memory_type,
        "min_capacity": min_capacity,
        "min_price": min_price,
        "max_price": max_price,
    }
    return list_rams(filters, limit, offset)


@router.get("/{product_id}")
def get_ram(product_id: int):
    data = get_ram_details(product_id)
    if not data:
        raise HTTPException(404, "RAM not found")
    return data
