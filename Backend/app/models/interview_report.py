from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class InterviewReport(Base):
    __tablename__ = "interview_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    job_description = Column(Text, nullable=False)
    resume = Column(Text, nullable=True)
    self_description = Column(Text, nullable=True)
    match_score = Column(Integer, default=0)

    # JSON columns for structured questions, gaps, and roadmap
    technical_questions = Column(JSON, default=list)
    behavioral_questions = Column(JSON, default=list)
    skill_gaps = Column(JSON, default=list)
    preparation_plan = Column(JSON, default=list)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="reports")
