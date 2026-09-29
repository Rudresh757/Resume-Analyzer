from datetime import datetime
from typing import Literal, Optional, List, Any
from pydantic import BaseModel, Field

class TechnicalQuestion(BaseModel):
    question: str
    intention: str
    answer: str

class BehavioralQuestion(BaseModel):
    question: str
    intention: str
    answer: str

class SkillGap(BaseModel):
    skill: str
    severity: Literal["low", "medium", "high"]

class PreparationPlanDay(BaseModel):
    day: int
    focus: str
    tasks: List[str]

class InterviewReportAIOutput(BaseModel):
    matchScore: int = Field(..., ge=0, le=100)
    technicalQuestions: List[TechnicalQuestion]
    behavioralQuestions: List[BehavioralQuestion]
    skillGaps: List[SkillGap]
    preparationPlan: List[PreparationPlanDay]
    title: str

class InterviewReportResponse(BaseModel):
    id: int
    _id: str
    title: str
    jobDescription: str
    resume: Optional[str] = None
    selfDescription: Optional[str] = None
    matchScore: int = 0
    technicalQuestions: List[TechnicalQuestion] = []
    behavioralQuestions: List[BehavioralQuestion] = []
    skillGaps: List[SkillGap] = []
    preparationPlan: List[PreparationPlanDay] = []
    user: Optional[int | str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }

    @classmethod
    def from_orm_model(cls, model: Any) -> "InterviewReportResponse":
        return cls(
            id=model.id,
            _id=str(model.id),
            title=model.title,
            jobDescription=model.job_description,
            resume=model.resume,
            selfDescription=model.self_description,
            matchScore=model.match_score,
            technicalQuestions=model.technical_questions or [],
            behavioralQuestions=model.behavioral_questions or [],
            skillGaps=model.skill_gaps or [],
            preparationPlan=model.preparation_plan or [],
            user=model.user_id,
            createdAt=model.created_at,
            updatedAt=model.updated_at
        )

class InterviewReportSummaryResponse(BaseModel):
    id: int
    _id: str
    title: str
    matchScore: int
    createdAt: Optional[datetime] = None

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }

    @classmethod
    def from_orm_model(cls, model: Any) -> "InterviewReportSummaryResponse":
        return cls(
            id=model.id,
            _id=str(model.id),
            title=model.title,
            matchScore=model.match_score,
            createdAt=model.created_at
        )

class GenerateReportResponse(BaseModel):
    message: str
    interviewReport: InterviewReportResponse

class GetReportByIdResponse(BaseModel):
    message: str
    interviewReport: InterviewReportResponse

class GetAllReportsResponse(BaseModel):
    message: str
    interviewReports: List[InterviewReportSummaryResponse]
