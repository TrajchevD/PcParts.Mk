from fastapi import APIRouter, HTTPException, Query

from app.repositories.parts import get_storage_details, search_storage

router = APIRouter(prefix="/api/products/storage", tags=["Storage"])


@router.get("")
def list_storage(
    search: str | None = None,
    sort: str = "price_asc",
    limit: int = Query(24, ge=1, le=200),
    offset: int = Query(0, ge=0),
    type: str | None = None,
    interface: str | None = None,
    capacity_gb: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
):
    filters = {
        k: v for k, v in {
            "type": type,
            "interface": interface,
            "capacity_gb": capacity_gb,
            "min_price": min_price,
            "max_price": max_price,
        }.items() if v is not None
    }
    return search_storage(search, filters, sort, limit, offset)


@router.get("/{product_id}")
def storage_details(product_id: int):
    data = get_storage_details(product_id)
    if not data:
        raise HTTPException(404, "Storage not found")
    return data
