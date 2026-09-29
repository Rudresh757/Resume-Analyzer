import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.interview_report import InterviewReport
from app.middlewares.auth import get_current_user
from app.services.pdf_service import parse_pdf_to_text
from app.services.ai_service import generate_interview_report, generate_resume_pdf
from app.schemas.interview import (
    GenerateReportResponse,
    GetReportByIdResponse,
    GetAllReportsResponse,
    InterviewReportResponse,
    InterviewReportSummaryResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/interview", tags=["Interview Strategy"])

@router.post("/", response_model=GenerateReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_interview_report_route(
    jobDescription: str = Form(...),
    selfDescription: Optional[str] = Form(None),
    resume: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new interview report based on user self-description, uploaded resume PDF, and job description.
    """
    resume_text: Optional[str] = None

    if resume and resume.filename:
        # Validate file size or extension if desired
        resume_bytes = await resume.read()
        if len(resume_bytes) > 0:
            try:
                resume_text = parse_pdf_to_text(resume_bytes)
            except Exception as e:
                logger.error(f"Error parsing resume PDF: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to parse uploaded PDF resume: {str(e)}"
                )

    if not resume_text and not selfDescription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either a Resume PDF or a Self Description must be provided."
        )

    try:
        # Call Gemini AI to produce structured analysis
        ai_report = await generate_interview_report(
            resume=resume_text,
            self_description=selfDescription,
            job_description=jobDescription
        )
    except Exception as e:
        logger.error(f"Gemini AI report generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )

    # Save to MySQL using SQLAlchemy
    new_report = InterviewReport(
        user_id=current_user.id,
        title=ai_report.get("title") or "Interview Strategy",
        job_description=jobDescription,
        resume=resume_text,
        self_description=selfDescription,
        match_score=ai_report.get("matchScore", 0),
        technical_questions=ai_report.get("technicalQuestions", []),
        behavioral_questions=ai_report.get("behavioralQuestions", []),
        skill_gaps=ai_report.get("skillGaps", []),
        preparation_plan=ai_report.get("preparationPlan", [])
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return GenerateReportResponse(
        message="Interview report generated successfully.",
        interviewReport=InterviewReportResponse.from_orm_model(new_report)
    )

@router.get("/report/{interview_id}", response_model=GetReportByIdResponse, status_code=status.HTTP_200_OK)
async def get_interview_report_by_id(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed interview report by ID.
    """
    report = db.query(InterviewReport).filter(
        InterviewReport.id == interview_id,
        InterviewReport.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview report not found."
        )

    return GetReportByIdResponse(
        message="Interview report fetched successfully.",
        interviewReport=InterviewReportResponse.from_orm_model(report)
    )

@router.get("/", response_model=GetAllReportsResponse, status_code=status.HTTP_200_OK)
async def get_all_interview_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all interview reports created by the authenticated user.
    """
    reports = db.query(InterviewReport).filter(
        InterviewReport.user_id == current_user.id
    ).order_by(InterviewReport.created_at.desc()).all()

    return GetAllReportsResponse(
        message="Interview reports fetched successfully.",
        interviewReports=[InterviewReportSummaryResponse.from_orm_model(r) for r in reports]
    )

@router.post("/resume/pdf/{interview_report_id}", status_code=status.HTTP_200_OK)
async def generate_resume_pdf_route(
    interview_report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate ATS-friendly tailored resume PDF based on interview report details.
    """
    report = db.query(InterviewReport).filter(
        InterviewReport.id == interview_report_id,
        InterviewReport.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview report not found."
        )

    try:
        pdf_bytes = await generate_resume_pdf(
            resume=report.resume,
            self_description=report.self_description,
            job_description=report.job_description
        )
    except Exception as e:
        logger.error(f"Error generating resume PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate resume PDF: {str(e)}"
        )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=resume_{interview_report_id}.pdf"
        }
    )
