from fastapi import APIRouter
from .endpoints import (
    students,
    attendance,
    exams,
    fees,
    risk_assessment,
    counseling,
    notifications,
    data_import,
    auth,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])
api_router.include_router(exams.router, prefix="/exams", tags=["Exams"])
api_router.include_router(fees.router, prefix="/fees", tags=["Fees"])
api_router.include_router(
    risk_assessment.router, prefix="/risk-assessment", tags=["Risk Assessment"]
)
api_router.include_router(counseling.router, prefix="/counseling", tags=["Counseling"])
api_router.include_router(
    notifications.router, prefix="/notifications", tags=["Notifications"]
)
api_router.include_router(
    data_import.router, prefix="/data-import", tags=["Data Import"]
)
