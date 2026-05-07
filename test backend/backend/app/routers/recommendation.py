# app/routers/recommendation.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.recommendation_service import recommend_build

router = APIRouter(prefix="/api/recommend", tags=["Recommendation"])

class RecommendationRequest(BaseModel):
    budget: int
    profile: str  # esports | aaa | school

@router.post("")
def generate_recommendation(body: RecommendationRequest):
    try:
        return recommend_build(body.budget, body.profile)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        # keep it simple (student-level), but still safe
        raise HTTPException(500, f"Recommendation error: {e}")