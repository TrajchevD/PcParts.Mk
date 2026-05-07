from fastapi import APIRouter, HTTPException, Query

from app.repositories.parts import get_ram_details, search_ram

router = APIRouter(prefix="/api/products/ram", tags=["RAM"])


@router.get("")
def list_ram(
    search: str | None = None,
    sort: str = "price_asc",
    limit: int = Query(24, ge=1, le=200),
    offset: int = Query(0, ge=0),
    memory_type: str | None = None,
    capacity_gb: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
):
    filters = {
        k: v for k, v in {
            "memory_type": memory_type,
            "capacity_gb": capacity_gb,
            "min_price": min_price,
            "max_price": max_price,
        }.items() if v is not None
    }
    return search_ram(search, None, filters, sort, limit, offset)


@router.get("/{product_id}")
def ram_details(product_id: int):
    data = get_ram_details(product_id)
    if not data:
        raise HTTPException(404, "RAM not found")
    return data
