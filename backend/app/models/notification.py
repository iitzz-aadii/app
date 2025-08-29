from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    Enum,
    Boolean,
    JSON,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class NotificationType(str, enum.Enum):
    RISK_ALERT = "risk_alert"
    COUNSELING_REMINDER = "counseling_reminder"
    FEE_REMINDER = "fee_reminder"
    ATTENDANCE_WARNING = "attendance_warning"
    ACADEMIC_WARNING = "academic_warning"
    SYSTEM_UPDATE = "system_update"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    IN_APP = "in_app"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    # Recipients
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)

    # Notification details
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)

    # Status and delivery
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    sent_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)

    # Metadata
    priority = Column(String, default="normal")  # low, normal, high, urgent
    metadata = Column(
        JSON, nullable=True
    )  # Additional data like risk scores, links, etc.

    # Retry logic
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")
    student = relationship("Student")

    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.type}', status='{self.status}', channel='{self.channel}')>"
