from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String, nullable=True)
    address = Column(Text, nullable=True)

    # Academic Information
    class_name = Column(String, nullable=False)
    section = Column(String, nullable=True)
    academic_year = Column(String, nullable=False)
    enrollment_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)

    # Guardian Information
    guardian_name = Column(String, nullable=True)
    guardian_phone = Column(String, nullable=True)
    guardian_email = Column(String, nullable=True)
    guardian_relationship = Column(String, nullable=True)

    # Mentor Assignment
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    mentor = relationship("User", back_populates="students")
    attendance_records = relationship("Attendance", back_populates="student")
    exam_scores = relationship("ExamScore", back_populates="student")
    fee_records = relationship("Fee", back_populates="student")
    risk_assessments = relationship("RiskAssessment", back_populates="student")
    counseling_sessions = relationship("CounselingSession", back_populates="student")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Student(id={self.id}, student_id='{self.student_id}', name='{self.full_name}')>"
