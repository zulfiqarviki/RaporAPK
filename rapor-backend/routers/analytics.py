from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth_dependency import get_current_user
from models.user import User
from schemas.analytics import (
    ComponentAveragesOut,
    StudentComparisonOut,
    StudentComparisonRequest,
    StudentProgressOut,
)
from services.analytics import (
    compare_students,
    get_component_averages,
    get_student_progress,
)


router = APIRouter(tags=["Analytics"])


@router.get(
    "/grade-tables/{grade_table_id}/analytics/component-averages",
    response_model=ComponentAveragesOut,
)
def get_grade_table_component_averages(
    grade_table_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_component_averages(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )


@router.get(
    "/grade-tables/{grade_table_id}/analytics/students/{student_id}/progress",
    response_model=StudentProgressOut,
)
def get_grade_table_student_progress(
    grade_table_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_student_progress(
        grade_table_id=grade_table_id,
        student_id=student_id,
        current_user=current_user,
        db=db,
    )


@router.post(
    "/grade-tables/{grade_table_id}/analytics/student-comparison",
    response_model=StudentComparisonOut,
)
def compare_grade_table_students(
    grade_table_id: int,
    comparison_data: StudentComparisonRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return compare_students(
        grade_table_id=grade_table_id,
        comparison_data=comparison_data,
        current_user=current_user,
        db=db,
    )