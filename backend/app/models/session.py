"""
Session SQLAlchemy model.

Stores each tutoring session: the problem presented, student's code submission,
execution results, Socratic hints, and outcome.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    concept_id = Column(String(50), nullable=False)
    difficulty_level = Column(Integer, nullable=False)
    problem_json = Column(JSONB, nullable=False)
    submitted_code = Column(Text, nullable=True)
    execution_result = Column(JSONB, nullable=True)
    socratic_hints = Column(JSONB, nullable=True, default=list)
    outcome = Column(String(20), nullable=True)  # "pass", "fail", "error"
    teacher_directive = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="sessions")

    def __repr__(self) -> str:
        return (
            f"<Session(id={self.id}, user_id={self.user_id}, "
            f"concept={self.concept_id!r}, outcome={self.outcome!r})>"
        )
