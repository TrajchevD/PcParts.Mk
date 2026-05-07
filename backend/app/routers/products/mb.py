from fastapi import APIRouter, HTTPException, Query

from app.repositories.parts import get_mb_details, search_mbs

router = APIRouter(prefix="/api/products/mb", tags=["Motherboards"])


@router.get("")
def list_motherboards(
    search: str | None = None,
    sort: str = "price_asc",
    limit: int = Query(24, ge=1, le=200),
    offset: int = Query(0, ge=0),
    socket: str | None = None,
    memory_type: str | None = None,
    form_factor: str | None = None,
    chipset: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
):
    filters = {
        k: v for k, v in {
            "socket": socket,
            "memory_type": memory_type,
            "form_factor": form_factor,
            "chipset": chipset,
            "min_price": min_price,
            "max_price": max_price,
        }.items() if v is not None
    }
    return search_mbs(search, None, None, filters, sort, limit, offset)


@router.get("/{product_id}")
def mb_details(product_id: int):
    data = get_mb_details(product_id)
    if not data:
        raise HTTPException(404, "Motherboard not found")
    return data
