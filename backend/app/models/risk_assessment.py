from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Float,
    DateTime,
    ForeignKey,
    Text,
    Enum,
    JSON,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class RiskLevel(str, enum.Enum):
    GREEN = "green"  # Safe
    YELLOW = "yellow"  # Warning
    RED = "red"  # Critical


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    assessment_date = Column(Date, nullable=False)

    # Rule-based assessment
    attendance_risk = Column(Enum(RiskLevel), nullable=False)
    academic_risk = Column(Enum(RiskLevel), nullable=False)
    financial_risk = Column(Enum(RiskLevel), nullable=False)
    overall_risk = Column(Enum(RiskLevel), nullable=False)

    # ML predictions
    dropout_probability = Column(Float, nullable=True)  # 0.0 to 1.0
    ml_risk_level = Column(Enum(RiskLevel), nullable=True)
    ml_confidence = Column(Float, nullable=True)

    # Risk factors and scores
    attendance_percentage = Column(Float, nullable=True)
    average_score = Column(Float, nullable=True)
    failed_subjects_count = Column(Integer, nullable=True)
    overdue_fees_count = Column(Integer, nullable=True)

    # Feature importance (JSON)
    feature_importance = Column(JSON, nullable=True)

    # Risk factors breakdown
    risk_factors = Column(JSON, nullable=True)  # List of specific risk factors

    # Recommendations
    recommendations = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="risk_assessments")

    def __repr__(self):
        return f"<RiskAssessment(student_id={self.student_id}, date='{self.assessment_date}', overall_risk='{self.overall_risk}')>"
