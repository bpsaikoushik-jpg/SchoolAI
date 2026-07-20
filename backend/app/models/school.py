from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.models.base import AuditMixin, Base

class School(Base, AuditMixin):
    __tablename__ = "schools"

    name = Column(String, nullable=False, index=True)
    address = Column(Text)
    phone = Column(String)
    website = Column(String)

    users = relationship("User", back_populates="school")
    classes = relationship("Class", back_populates="school")
