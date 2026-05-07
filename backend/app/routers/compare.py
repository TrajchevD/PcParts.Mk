from fastapi import APIRouter, HTTPException

from app.schemas.products import CompareRequest
from app.services.compare import compare_products

router = APIRouter(prefix="/api/compare", tags=["compare"])


@router.post("")
def compare(body: CompareRequest):
    if not body.ids or len(body.ids) < 2:
        raise HTTPException(400, "Provide at least 2 product ids to compare")
    try:
        items = compare_products(body.category, body.ids)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    return {"category": body.category, "items": items}
