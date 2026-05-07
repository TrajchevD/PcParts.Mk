from fastapi import APIRouter, HTTPException, Query

from app.repositories.parts import get_cpu_details, list_grouped_cpus

router = APIRouter(prefix="/api/products/cpu", tags=["CPU"])


@router.get("")
def list_cpus(
    search: str | None = None,
    sort: str = "price_asc",
    limit: int = Query(24, ge=1, le=200),
    offset: int = Query(0, ge=0),
    brand: str | None = None,
    socket: str | None = None,
    min_cores: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
):
    filters = {
        k: v for k, v in {
            "brand": brand,
            "socket": socket,
            "min_cores": min_cores,
            "min_price": min_price,
            "max_price": max_price,
        }.items() if v is not None
    }
    return list_grouped_cpus(search, filters, sort, limit, offset)


@router.get("/{cpu_model:path}")
def cpu_details(cpu_model: str):
    data = get_cpu_details(cpu_model)
    if not data:
        raise HTTPException(404, "CPU not found")
    return data
