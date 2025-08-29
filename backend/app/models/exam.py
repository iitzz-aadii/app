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
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class ExamType(str, enum.Enum):
    MIDTERM = "midterm"
    FINAL = "final"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    PROJECT = "project"


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    exam_name = Column(String, nullable=False)
    exam_type = Column(Enum(ExamType), nullable=False)
    subject = Column(String, nullable=False)
    class_name = Column(String, nullable=False)
    exam_date = Column(Date, nullable=False)
    total_marks = Column(Float, nullable=False)
    passing_marks = Column(Float, nullable=False)
    description = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    scores = relationship("ExamScore", back_populates="exam")

    def __repr__(self):
        return f"<Exam(id={self.id}, name='{self.exam_name}', subject='{self.subject}', date='{self.exam_date}')>"


class ExamScore(Base):
    __tablename__ = "exam_scores"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    marks_obtained = Column(Float, nullable=False)
    remarks = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="exam_scores")
    exam = relationship("Exam", back_populates="scores")

    @property
    def percentage(self):
        if self.exam and self.exam.total_marks > 0:
            return (self.marks_obtained / self.exam.total_marks) * 100
        return 0

    @property
    def is_passed(self):
        if self.exam:
            return self.marks_obtained >= self.exam.passing_marks
        return False

    def __repr__(self):
        return f"<ExamScore(student_id={self.student_id}, exam_id={self.exam_id}, marks={self.marks_obtained})>"
