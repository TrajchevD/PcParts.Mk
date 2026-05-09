from fastapi import APIRouter, HTTPException

from app.schemas.products import CompareRequest
from app.services.compare import compare_products

router = APIRouter(prefix="/api/compare", tags=["compare"])


@router.post("")
def compare(body: CompareRequest):
    if not body.ids:
        raise HTTPException(400, "Provide at least one product id")
    try:
        items = compare_products(body.category, body.ids)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    return {"category": body.category, "items": items}
