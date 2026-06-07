from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth_dependency import get_current_user
from models.user import User
from schemas.score import ScoreCreate, ScoreOut, ScoreUpdate
from services.score import (
    create_score,
    delete_score,
    get_score_by_id,
    list_scores,
    update_score,
)


router = APIRouter(tags=["Scores"])


@router.get(
    "/grade-tables/{grade_table_id}/scores",
    response_model=list[ScoreOut],
)
def get_grade_table_scores(
    grade_table_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_scores(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )


@router.post(
    "/grade-tables/{grade_table_id}/scores",
    response_model=ScoreOut,
    status_code=status.HTTP_201_CREATED,
)
def create_grade_table_score(
    grade_table_id: int,
    score_data: ScoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_score(
        grade_table_id=grade_table_id,
        score_data=score_data,
        current_user=current_user,
        db=db,
    )


@router.get(
    "/scores/{score_id}",
    response_model=ScoreOut,
)
def get_score_detail(
    score_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_score_by_id(
        score_id=score_id,
        current_user=current_user,
        db=db,
    )


@router.patch(
    "/scores/{score_id}",
    response_model=ScoreOut,
)
def update_score_detail(
    score_id: int,
    score_data: ScoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_score(
        score_id=score_id,
        score_data=score_data,
        current_user=current_user,
        db=db,
    )


@router.delete(
    "/scores/{score_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_score_detail(
    score_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_score(
        score_id=score_id,
        current_user=current_user,
        db=db,
    )