from fastapi import APIRouter, HTTPException, Query

from app.repositories.parts import get_gpu_details, list_grouped_gpus

router = APIRouter(prefix="/api/products/gpu", tags=["GPU"])


@router.get("")
def list_gpus(
    search: str | None = None,
    sort: str = "price_asc",
    limit: int = Query(24, ge=1, le=200),
    offset: int = Query(0, ge=0),
    brand: str | None = None,
    min_vram: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
):
    filters = {
        k: v for k, v in {
            "brand": brand,
            "min_vram": min_vram,
            "min_price": min_price,
            "max_price": max_price,
        }.items() if v is not None
    }
    return list_grouped_gpus(search, filters, sort, limit, offset)


@router.get("/{gpu_model:path}")
def gpu_details(gpu_model: str):
    data = get_gpu_details(gpu_model)
    if not data:
        raise HTTPException(404, "GPU not found")
    return data
