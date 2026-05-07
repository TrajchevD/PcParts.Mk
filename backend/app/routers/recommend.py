from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from app.services.recommendation import PROFILE_ALLOCATIONS, recommend_build

router = APIRouter(prefix="/api/recommend", tags=["recommend"])


class RecommendRequest(BaseModel):
    budget: int
    profile: str

    @field_validator("budget")
    @classmethod
    def budget_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("budget must be a positive integer")
        return v

    @field_validator("profile")
    @classmethod
    def valid_profile(cls, v: str) -> str:
        if v not in PROFILE_ALLOCATIONS:
            raise ValueError(f"profile must be one of {list(PROFILE_ALLOCATIONS)}")
        return v


@router.post("")
def generate_recommendation(body: RecommendRequest):
    try:
        return recommend_build(body.budget, body.profile)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:
        raise HTTPException(500, f"Recommendation failed: {exc}")
