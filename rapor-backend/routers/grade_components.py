from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth_dependency import get_current_user
from models.user import User
from schemas.grade_component import (
    GradeComponentCreate,
    GradeComponentOut,
    GradeComponentUpdate,
)
from services.grade_component import (
    create_component,
    delete_component,
    get_component_by_id,
    list_components,
    update_component,
)


router = APIRouter(tags=["Grade Components"])


@router.get(
    "/grade-tables/{grade_table_id}/components",
    response_model=list[GradeComponentOut],
)
def get_grade_table_components(
    grade_table_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_components(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )


@router.post(
    "/grade-tables/{grade_table_id}/components",
    response_model=GradeComponentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_grade_table_component(
    grade_table_id: int,
    component_data: GradeComponentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_component(
        grade_table_id=grade_table_id,
        component_data=component_data,
        current_user=current_user,
        db=db,
    )


@router.get(
    "/grade-components/{component_id}",
    response_model=GradeComponentOut,
)
def get_grade_component_detail(
    component_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_component_by_id(
        component_id=component_id,
        current_user=current_user,
        db=db,
    )


@router.patch(
    "/grade-components/{component_id}",
    response_model=GradeComponentOut,
)
def update_grade_component_detail(
    component_id: int,
    component_data: GradeComponentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_component(
        component_id=component_id,
        component_data=component_data,
        current_user=current_user,
        db=db,
    )


@router.delete(
    "/grade-components/{component_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_grade_component_detail(
    component_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_component(
        component_id=component_id,
        current_user=current_user,
        db=db,
    )