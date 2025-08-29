from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta

from ....core.database import get_db
from ....models import Student, RiskAssessment, User
from ....ml.risk_assessor import RiskAssessor
from ....schemas.risk_assessment import (
    RiskAssessmentCreate,
    RiskAssessmentResponse,
    RiskSummaryResponse,
    RiskLevel,
    StudentRiskProfile,
)
from ....core.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[RiskAssessmentResponse])
async def get_risk_assessments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    risk_level: Optional[RiskLevel] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all risk assessments with optional filtering"""
    query = db.query(RiskAssessment)

    if risk_level:
        query = query.filter(RiskAssessment.overall_risk == risk_level)

    if date_from:
        query = query.filter(RiskAssessment.assessment_date >= date_from)

    if date_to:
        query = query.filter(RiskAssessment.assessment_date <= date_to)

    assessments = query.offset(skip).limit(limit).all()
    return assessments


@router.get("/summary", response_model=RiskSummaryResponse)
async def get_risk_summary(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get overall risk summary statistics"""
    total_assessments = db.query(RiskAssessment).count()

    green_count = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.overall_risk == RiskLevel.GREEN)
        .count()
    )

    yellow_count = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.overall_risk == RiskLevel.YELLOW)
        .count()
    )

    red_count = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.overall_risk == RiskLevel.RED)
        .count()
    )

    # Get recent assessments (last 30 days)
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_assessments = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.assessment_date >= thirty_days_ago)
        .count()
    )

    return RiskSummaryResponse(
        total_assessments=total_assessments,
        green_count=green_count,
        yellow_count=yellow_count,
        red_count=red_count,
        recent_assessments=recent_assessments,
        risk_distribution={
            "green": green_count,
            "yellow": yellow_count,
            "red": red_count,
        },
    )


@router.get("/student/{student_id}", response_model=StudentRiskProfile)
async def get_student_risk_profile(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get comprehensive risk profile for a specific student"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )

    # Get latest risk assessment
    latest_assessment = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.student_id == student_id)
        .order_by(RiskAssessment.assessment_date.desc())
        .first()
    )

    # Get risk history
    risk_history = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.student_id == student_id)
        .order_by(RiskAssessment.assessment_date.desc())
        .limit(10)
        .all()
    )

    return StudentRiskProfile(
        student=student, latest_assessment=latest_assessment, risk_history=risk_history
    )


@router.post("/assess/{student_id}", response_model=RiskAssessmentResponse)
async def assess_student_risk(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Perform risk assessment for a specific student"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )

    # Initialize risk assessor
    risk_assessor = RiskAssessor()

    # Perform assessment
    assessment_result = risk_assessor.assess_student_risk(student, db)

    # Create risk assessment record
    risk_assessment = RiskAssessment(
        student_id=student_id,
        assessment_date=assessment_result["assessment_date"],
        attendance_risk=assessment_result["rule_based_risk"]["attendance"],
        academic_risk=assessment_result["rule_based_risk"]["academic"],
        financial_risk=assessment_result["rule_based_risk"]["financial"],
        overall_risk=assessment_result["rule_based_risk"]["overall"],
        dropout_probability=assessment_result["ml_prediction"]["dropout_probability"],
        ml_risk_level=assessment_result["ml_risk_level"],
        ml_confidence=assessment_result["ml_prediction"]["confidence"],
        attendance_percentage=assessment_result["features"].get(
            "attendance_percentage"
        ),
        average_score=assessment_result["features"].get("average_score"),
        failed_subjects_count=assessment_result["features"].get("failed_exams"),
        overdue_fees_count=assessment_result["features"].get("overdue_fees_count"),
        feature_importance=assessment_result["ml_prediction"].get("model_predictions"),
        risk_factors=assessment_result.get("risk_factors", []),
        recommendations="\n".join(assessment_result["recommendations"]),
    )

    db.add(risk_assessment)
    db.commit()
    db.refresh(risk_assessment)

    return risk_assessment


@router.post("/assess-all")
async def assess_all_students_risk(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Perform risk assessment for all active students"""
    if current_user.role not in ["admin", "mentor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    active_students = db.query(Student).filter(Student.is_active == True).all()

    if not active_students:
        return {"message": "No active students found", "assessments_created": 0}

    risk_assessor = RiskAssessor()
    assessments_created = 0

    for student in active_students:
        try:
            # Check if assessment already exists for today
            existing_assessment = (
                db.query(RiskAssessment)
                .filter(
                    RiskAssessment.student_id == student.id,
                    RiskAssessment.assessment_date == datetime.now().date(),
                )
                .first()
            )

            if existing_assessment:
                continue

            # Perform assessment
            assessment_result = risk_assessor.assess_student_risk(student, db)

            # Create risk assessment record
            risk_assessment = RiskAssessment(
                student_id=student.id,
                assessment_date=assessment_result["assessment_date"],
                attendance_risk=assessment_result["rule_based_risk"]["attendance"],
                academic_risk=assessment_result["rule_based_risk"]["academic"],
                financial_risk=assessment_result["rule_based_risk"]["financial"],
                overall_risk=assessment_result["rule_based_risk"]["overall"],
                dropout_probability=assessment_result["ml_prediction"][
                    "dropout_probability"
                ],
                ml_risk_level=assessment_result["ml_risk_level"],
                ml_confidence=assessment_result["ml_prediction"]["confidence"],
                attendance_percentage=assessment_result["features"].get(
                    "attendance_percentage"
                ),
                average_score=assessment_result["features"].get("average_score"),
                failed_subjects_count=assessment_result["features"].get("failed_exams"),
                overdue_fees_count=assessment_result["features"].get(
                    "overdue_fees_count"
                ),
                feature_importance=assessment_result["ml_prediction"].get(
                    "model_predictions"
                ),
                risk_factors=assessment_result.get("risk_factors", []),
                recommendations="\n".join(assessment_result["recommendations"]),
            )

            db.add(risk_assessment)
            assessments_created += 1

        except Exception as e:
            # Log error but continue with other students
            print(f"Error assessing student {student.id}: {e}")
            continue

    try:
        db.commit()
        return {
            "message": f"Risk assessment completed for {len(active_students)} students",
            "assessments_created": assessments_created,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving assessments: {str(e)}",
        )


@router.get("/high-risk", response_model=List[StudentRiskProfile])
async def get_high_risk_students(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get students with high risk (yellow or red)"""
    # Get latest assessment for each student
    latest_assessments = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.overall_risk.in_([RiskLevel.YELLOW, RiskLevel.RED]))
        .order_by(RiskAssessment.assessment_date.desc())
        .limit(limit)
        .all()
    )

    # Get unique students and their latest assessments
    student_ids = list(set([ra.student_id for ra in latest_assessments]))
    high_risk_students = []

    for student_id in student_ids:
        student = db.query(Student).filter(Student.id == student_id).first()
        if student:
            latest_assessment = (
                db.query(RiskAssessment)
                .filter(RiskAssessment.student_id == student_id)
                .order_by(RiskAssessment.assessment_date.desc())
                .first()
            )

            high_risk_students.append(
                StudentRiskProfile(
                    student=student,
                    latest_assessment=latest_assessment,
                    risk_history=[],
                )
            )

    return high_risk_students


@router.delete("/{assessment_id}")
async def delete_risk_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a specific risk assessment"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete risk assessments",
        )

    assessment = (
        db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()
    )
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Risk assessment not found"
        )

    db.delete(assessment)
    db.commit()

    return {"message": "Risk assessment deleted successfully"}
