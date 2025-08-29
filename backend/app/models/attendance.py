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


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(Date, nullable=False)
    subject = Column(String, nullable=False)
    is_present = Column(Boolean, nullable=False)
    remarks = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="attendance_records")

    def __repr__(self):
        status = "Present" if self.is_present else "Absent"
        return f"<Attendance(student_id={self.student_id}, date='{self.date}', subject='{self.subject}', status='{status}')>"
