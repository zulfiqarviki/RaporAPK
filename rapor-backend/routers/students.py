from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth_dependency import get_current_user
from models.user import User
from schemas.student import StudentCreate, StudentOut, StudentUpdate
from services.student import (
    create_student,
    delete_student,
    get_student_by_id,
    list_students,
    update_student,
)


router = APIRouter(tags=["Students"])


@router.get(
    "/grade-tables/{grade_table_id}/students",
    response_model=list[StudentOut],
)
def get_grade_table_students(
    grade_table_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_students(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )


@router.post(
    "/grade-tables/{grade_table_id}/students",
    response_model=StudentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_grade_table_student(
    grade_table_id: int,
    student_data: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_student(
        grade_table_id=grade_table_id,
        student_data=student_data,
        current_user=current_user,
        db=db,
    )


@router.get(
    "/students/{student_id}",
    response_model=StudentOut,
)
def get_student_detail(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_student_by_id(
        student_id=student_id,
        current_user=current_user,
        db=db,
    )


@router.patch(
    "/students/{student_id}",
    response_model=StudentOut,
)
def update_student_detail(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_student(
        student_id=student_id,
        student_data=student_data,
        current_user=current_user,
        db=db,
    )


@router.delete(
    "/students/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_student_detail(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_student(
        student_id=student_id,
        current_user=current_user,
        db=db,
    )