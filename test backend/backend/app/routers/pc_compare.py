from fastapi import APIRouter, HTTPException
from app.db import fetchall
from app.services.compare.compare_service import compare_products

router = APIRouter(prefix="/api/compare", tags=["compare"])

@router.post("")
def compare_api(payload: dict):
    category = payload.get("category")
    ids = payload.get("ids")  # ✅ CHANGE HERE

    if not category or not ids or len(ids) < 1:
        raise HTTPException(400, "Select at least 1 item")

    data = compare_products(category, ids)

    return {
        "category": category,
        "items": data,
    }
