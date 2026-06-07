from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.grade_component import GradeComponent
from models.user import User
from schemas.grade_component import GradeComponentCreate, GradeComponentUpdate
from services.grade_table import get_grade_table_by_id


def list_components(
    grade_table_id: int,
    current_user: User,
    db: Session,
) -> list[GradeComponent]:
    grade_table = get_grade_table_by_id(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )

    return (
        db.query(GradeComponent)
        .filter(GradeComponent.grade_table_id == grade_table.id)
        .order_by(GradeComponent.order_index.asc(), GradeComponent.id.asc())
        .all()
    )


def get_component_by_id(
    component_id: int,
    current_user: User,
    db: Session,
) -> GradeComponent:
    component = (
        db.query(GradeComponent)
        .filter(GradeComponent.id == component_id)
        .first()
    )

    if component is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade component not found",
        )

    get_grade_table_by_id(
        grade_table_id=component.grade_table_id,
        current_user=current_user,
        db=db,
    )

    return component


def create_component(
    grade_table_id: int,
    component_data: GradeComponentCreate,
    current_user: User,
    db: Session,
) -> GradeComponent:
    grade_table = get_grade_table_by_id(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )

    component = GradeComponent(
        name=component_data.name,
        weight=component_data.weight,
        max_score=100,
        order_index=component_data.order_index,
        grade_table_id=grade_table.id,
    )

    db.add(component)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Component name already exists in this grade table",
        )

    db.refresh(component)

    return component


def update_component(
    component_id: int,
    component_data: GradeComponentUpdate,
    current_user: User,
    db: Session,
) -> GradeComponent:
    component = get_component_by_id(
        component_id=component_id,
        current_user=current_user,
        db=db,
    )

    if component_data.name is not None:
        component.name = component_data.name

    if component_data.weight is not None:
        component.weight = component_data.weight

    if component_data.order_index is not None:
        component.order_index = component_data.order_index

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Component name already exists in this grade table",
        )

    db.refresh(component)

    return component


def delete_component(
    component_id: int,
    current_user: User,
    db: Session,
) -> None:
    component = get_component_by_id(
        component_id=component_id,
        current_user=current_user,
        db=db,
    )

    db.delete(component)
    db.commit()