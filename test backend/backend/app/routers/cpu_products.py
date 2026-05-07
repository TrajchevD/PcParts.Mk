from fastapi import APIRouter, Query, HTTPException
from app.services.cpu_products_service import (
    list_grouped_cpus,
    get_cpu_details,
)
from pydantic import BaseModel
from typing import Optional, Dict

class CpuListRequest(BaseModel):
    search: Optional[str] = None
    sort: str = "price_asc"
    limit: int = 24
    offset: int = 0
    filters: Dict = {}

router = APIRouter(prefix="/api/products/cpu", tags=["CPU Products"])

@router.get("")
def get_cpu_products(
    search: str | None = None,
    sort: str = "price_asc",
    limit: int = 24,
    offset: int = 0,
    brand: str | None = None,
    socket: str | None = None,
    min_cores: int | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
):
    filters = {
        "brand": brand,
        "socket": socket,
        "min_cores": min_cores,
        "min_price": min_price,
        "max_price": max_price,
    }

    return list_grouped_cpus(search, filters, sort, limit, offset)

@router.post("")
def post_cpu_products(req: CpuListRequest):
    return list_grouped_cpus(
        req.search,
        req.filters,
        req.sort,
        req.limit,
        req.offset,
    )

@router.get("/{cpu_model}")
def get_cpu_product_details(cpu_model: str):
    data = get_cpu_details(cpu_model)
    if not data:
        raise HTTPException(404, "CPU not found")

    return data
