from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth_dependency import require_admin
from models.user import User
from schemas.user import TeacherCreate, TeacherUpdate, UserOut
from services.admin import (
    create_teacher,
    delete_teacher,
    get_all_teachers,
    update_teacher,
)


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/teachers", response_model=list[UserOut])
def list_teachers(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    return get_all_teachers(db)


@router.post(
    "/teachers",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
def create_teacher_account(
    user_data: TeacherCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    return create_teacher(user_data=user_data, db=db)


@router.patch("/teachers/{teacher_id}", response_model=UserOut)
def update_teacher_account(
    teacher_id: int,
    user_data: TeacherUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    return update_teacher(
        teacher_id=teacher_id,
        user_data=user_data,
        db=db,
    )


@router.delete(
    "/teachers/{teacher_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_teacher_account(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    delete_teacher(teacher_id=teacher_id, db=db)