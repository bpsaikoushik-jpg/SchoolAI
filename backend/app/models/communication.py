from sqlalchemy import Column, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import AuditMixin, Base

class Notification(Base, AuditMixin):
    __tablename__ = "notifications"

    user_id = Column(ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    type = Column(String) # system, mentor, academic

    user = relationship("User", back_populates="notifications")
