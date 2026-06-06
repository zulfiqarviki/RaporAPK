from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth_dependency import get_current_user
from models.user import User
from schemas.result import GradeTableResultOut
from services.result import get_grade_table_results


router = APIRouter(tags=["Results"])


@router.get(
    "/grade-tables/{grade_table_id}/results",
    response_model=GradeTableResultOut,
)
def get_results(
    grade_table_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_grade_table_results(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )