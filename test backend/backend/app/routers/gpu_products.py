from fastapi import APIRouter, HTTPException
from app.services.gpu_products_service import list_grouped_gpus , get_gpu_details
from pydantic import BaseModel
from typing import Optional, Dict

router = APIRouter(prefix="/api/products/gpu", tags=["GPU Products"])

class GpuListRequest(BaseModel):
    search: Optional[str] = None
    sort: str = "price_asc"
    limit: int = 24
    offset: int = 0
    filters: Dict = {}

@router.post("")
def post_gpu_products(req: GpuListRequest):
    return list_grouped_gpus(
        req.search,
        req.filters,
        req.sort,
        req.limit,
        req.offset,
    )

@router.get("/{model}/{vram}")
def get_gpu_product_details(model: str, vram: int):
    data = get_gpu_details(model, vram)
    if not data:
        raise HTTPException(404, "GPU not found")
    return data
