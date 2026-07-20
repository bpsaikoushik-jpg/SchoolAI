"""
Calendar module.

Backs the Teacher/Principal calendar pages. Deliberately simple - a single
CalendarEvent table scoped to the school, with an optional class_id and
owner_id so events can be personal (e.g. "Grade quiz submissions") or
class-linked (e.g. a scheduled lesson).
"""
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import AuditMixin, Base


class CalendarEvent(Base, AuditMixin):
    __tablename__ = "calendar_events"

    school_id = Column(ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    class_id = Column(ForeignKey("classes.id", ondelete="SET NULL"), nullable=True, index=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(String, default="task")  # class, meeting, task, other
    starts_at = Column(DateTime(timezone=True), nullable=False, index=True)
    ends_at = Column(DateTime(timezone=True), nullable=True)

    school = relationship("School")
    owner = relationship("User")
    class_room = relationship("Class")
