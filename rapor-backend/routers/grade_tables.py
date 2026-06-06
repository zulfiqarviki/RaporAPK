from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth_dependency import get_current_user
from models.user import User
from schemas.grade_table import GradeTableCreate, GradeTableOut, GradeTableUpdate
from services.grade_table import (
    create_grade_table,
    delete_grade_table,
    get_grade_table_by_id,
    list_grade_tables,
    update_grade_table,
)


router = APIRouter(prefix="/grade-tables", tags=["Grade Tables"])


@router.get("/", response_model=list[GradeTableOut])
def get_grade_tables(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_grade_tables(
        current_user=current_user,
        db=db,
    )


@router.post(
    "/",
    response_model=GradeTableOut,
    status_code=status.HTTP_201_CREATED,
)
def create_new_grade_table(
    grade_table_data: GradeTableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_grade_table(
        grade_table_data=grade_table_data,
        current_user=current_user,
        db=db,
    )


@router.get("/{grade_table_id}", response_model=GradeTableOut)
def get_grade_table_detail(
    grade_table_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_grade_table_by_id(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )


@router.put("/{grade_table_id}", response_model=GradeTableOut)
def update_existing_grade_table(
    grade_table_id: int,
    grade_table_data: GradeTableUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_grade_table(
        grade_table_id=grade_table_id,
        grade_table_data=grade_table_data,
        current_user=current_user,
        db=db,
    )


@router.delete(
    "/{grade_table_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_existing_grade_table(
    grade_table_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_grade_table(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )