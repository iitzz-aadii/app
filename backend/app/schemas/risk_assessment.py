from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


class RiskLevel(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class RiskAssessmentBase(BaseModel):
    student_id: int
    assessment_date: date
    attendance_risk: RiskLevel
    academic_risk: RiskLevel
    financial_risk: RiskLevel
    overall_risk: RiskLevel


class RiskAssessmentCreate(RiskAssessmentBase):
    dropout_probability: Optional[float] = Field(None, ge=0.0, le=1.0)
    ml_risk_level: Optional[RiskLevel] = None
    ml_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    attendance_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    average_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    failed_subjects_count: Optional[int] = Field(None, ge=0)
    overdue_fees_count: Optional[int] = Field(None, ge=0)
    feature_importance: Optional[Dict[str, Any]] = None
    risk_factors: Optional[List[str]] = None
    recommendations: Optional[str] = None


class RiskAssessmentResponse(RiskAssessmentBase):
    id: int
    dropout_probability: Optional[float] = None
    ml_risk_level: Optional[RiskLevel] = None
    ml_confidence: Optional[float] = None
    attendance_percentage: Optional[float] = None
    average_score: Optional[float] = None
    failed_subjects_count: Optional[int] = None
    overdue_fees_count: Optional[int] = None
    feature_importance: Optional[Dict[str, Any]] = None
    risk_factors: Optional[List[str]] = None
    recommendations: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RiskSummaryResponse(BaseModel):
    total_assessments: int
    green_count: int
    yellow_count: int
    red_count: int
    recent_assessments: int
    risk_distribution: Dict[str, int]


class StudentBase(BaseModel):
    id: int
    student_id: str
    first_name: str
    last_name: str
    class_name: str
    section: Optional[str] = None
    academic_year: str
    is_active: bool

    class Config:
        from_attributes = True


class StudentRiskProfile(BaseModel):
    student: StudentBase
    latest_assessment: Optional[RiskAssessmentResponse] = None
    risk_history: List[RiskAssessmentResponse] = []


class RiskTrendData(BaseModel):
    date: date
    green_count: int
    yellow_count: int
    red_count: int
    total_count: int


class RiskAnalysisRequest(BaseModel):
    student_ids: Optional[List[int]] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    risk_levels: Optional[List[RiskLevel]] = None


class RiskAnalysisResponse(BaseModel):
    total_students: int
    risk_distribution: Dict[str, int]
    average_dropout_probability: float
    top_risk_factors: List[str]
    recommendations_summary: List[str]
    trend_data: List[RiskTrendData]
