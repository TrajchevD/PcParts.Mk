from fastapi import APIRouter, HTTPException
from app.services.mb_products_service import (
    list_motherboards,
    get_mb_details,
)

router = APIRouter(prefix="/api/products/mb", tags=["Motherboards"])

@router.get("")
def get_motherboards(
    socket: str | None = None,
    memory_type: str | None = None,
    form_factor: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    sort: str = "price_asc",
    limit: int = 24,
    offset: int = 0,
):
    filters = {
        "socket": socket,
        "memory_type": memory_type,
        "form_factor": form_factor,
        "min_price": min_price,
        "max_price": max_price,
    }

    return list_motherboards(filters, sort, limit, offset)


@router.get("/{product_id}")
def get_mb(product_id: int):
    data = get_mb_details(product_id)
    if not data:
        raise HTTPException(404, "Motherboard not found")
    return data
