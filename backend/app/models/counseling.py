from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey,
    Text,
    Enum,
    Boolean,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class SessionStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class InterventionType(str, enum.Enum):
    EXTRA_CLASSES = "extra_classes"
    PEER_MENTORING = "peer_mentoring"
    PARENT_MEETING = "parent_meeting"
    ACADEMIC_SUPPORT = "academic_support"
    FINANCIAL_AID = "financial_aid"
    COUNSELING = "counseling"
    OTHER = "other"


class CounselingSession(Base):
    __tablename__ = "counseling_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    counselor_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Session details
    session_date = Column(DateTime, nullable=False)
    session_type = Column(Enum(InterventionType), nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.SCHEDULED)

    # Session content
    agenda = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    outcomes = Column(Text, nullable=True)

    # Follow-up
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime, nullable=True)
    follow_up_notes = Column(Text, nullable=True)

    # Effectiveness tracking
    student_feedback = Column(Text, nullable=True)
    counselor_feedback = Column(Text, nullable=True)
    effectiveness_rating = Column(Integer, nullable=True)  # 1-5 scale

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="counseling_sessions")
    counselor = relationship("User", back_populates="counseling_sessions")

    def __repr__(self):
        return f"<CounselingSession(student_id={self.student_id}, counselor_id={self.counselor_id}, date='{self.session_date}', status='{self.status}')>"
