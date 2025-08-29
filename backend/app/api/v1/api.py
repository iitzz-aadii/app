from fastapi import APIRouter
from .endpoints import risk_assessment

api_router = APIRouter()

# Include only available endpoint routers for now
api_router.include_router(
    risk_assessment.router, prefix="/risk-assessment", tags=["Risk Assessment"]
)
