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
    Boolean,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class FeeStatus(str, enum.Enum):
    PAID = "paid"
    PARTIAL = "partial"
    UNPAID = "unpaid"
    OVERDUE = "overdue"


class Fee(Base):
    __tablename__ = "fees"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    fee_type = Column(String, nullable=False)  # e.g., "tuition", "library", "sports"
    amount_due = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0.0)
    due_date = Column(Date, nullable=False)
    payment_date = Column(Date, nullable=True)
    status = Column(Enum(FeeStatus), default=FeeStatus.UNPAID)
    is_overdue = Column(Boolean, default=False)
    remarks = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="fee_records")

    @property
    def balance(self):
        return self.amount_due - self.amount_paid

    @property
    def payment_percentage(self):
        if self.amount_due > 0:
            return (self.amount_paid / self.amount_due) * 100
        return 0

    def __repr__(self):
        return f"<Fee(student_id={self.student_id}, type='{self.fee_type}', status='{self.status}', balance={self.balance})>"
