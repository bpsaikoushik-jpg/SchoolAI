"""Parent <-> Student relationship.

This is the one genuinely missing model needed for Parent AI: nothing in the
existing schema recorded which student(s) belong to which parent. Everything
else the AI Intelligence Engine needs (memory, learning profile, weakness
profile, recommendations, tracking data) already exists.
"""
from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import AuditMixin, Base


class ParentStudentLink(Base, AuditMixin):
    __tablename__ = "parent_student_links"
    __table_args__ = (UniqueConstraint("parent_id", "student_id", name="uq_parent_student_link"),)

    parent_id = Column(ForeignKey("parent_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type = Column(String, default="guardian")  # mother, father, guardian, other

    parent = relationship("ParentProfile", back_populates="child_links", foreign_keys=[parent_id])
    student = relationship("StudentProfile", back_populates="parent_links", foreign_keys=[student_id])
