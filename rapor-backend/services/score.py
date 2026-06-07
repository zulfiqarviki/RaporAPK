from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.grade_component import GradeComponent
from models.score import Score
from models.student import Student
from models.user import User
from schemas.score import ScoreCreate, ScoreUpdate
from services.grade_table import get_grade_table_by_id


def get_student_and_component_or_404(
    grade_table_id: int,
    student_id: int,
    component_id: int,
    current_user: User,
    db: Session,
) -> tuple[Student, GradeComponent]:
    grade_table = get_grade_table_by_id(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )

    student = (
        db.query(Student)
        .filter(
            Student.id == student_id,
            Student.grade_table_id == grade_table.id,
        )
        .first()
    )

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found in this grade table",
        )

    component = (
        db.query(GradeComponent)
        .filter(
            GradeComponent.id == component_id,
            GradeComponent.grade_table_id == grade_table.id,
        )
        .first()
    )

    if component is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Component not found in this grade table",
        )

    return student, component


def list_scores(
    grade_table_id: int,
    current_user: User,
    db: Session,
) -> list[Score]:
    grade_table = get_grade_table_by_id(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )

    return (
        db.query(Score)
        .join(Student, Score.student_id == Student.id)
        .filter(Student.grade_table_id == grade_table.id)
        .order_by(Student.id.asc(), Score.component_id.asc())
        .all()
    )


def get_score_by_id(
    score_id: int,
    current_user: User,
    db: Session,
) -> Score:
    score = db.query(Score).filter(Score.id == score_id).first()

    if score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Score not found",
        )

    student = db.query(Student).filter(Student.id == score.student_id).first()

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    get_grade_table_by_id(
        grade_table_id=student.grade_table_id,
        current_user=current_user,
        db=db,
    )

    return score


def create_score(
    grade_table_id: int,
    score_data: ScoreCreate,
    current_user: User,
    db: Session,
) -> Score:
    student, component = get_student_and_component_or_404(
        grade_table_id=grade_table_id,
        student_id=score_data.student_id,
        component_id=score_data.component_id,
        current_user=current_user,
        db=db,
    )

    score = Score(
        student_id=student.id,
        component_id=component.id,
        score=score_data.score,
    )

    db.add(score)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Score for this student and component already exists",
        )

    db.refresh(score)

    return score


def update_score(
    score_id: int,
    score_data: ScoreUpdate,
    current_user: User,
    db: Session,
) -> Score:
    score = get_score_by_id(
        score_id=score_id,
        current_user=current_user,
        db=db,
    )

    if score_data.score is not None:
        score.score = score_data.score

    db.commit()
    db.refresh(score)

    return score


def delete_score(
    score_id: int,
    current_user: User,
    db: Session,
) -> None:
    score = get_score_by_id(
        score_id=score_id,
        current_user=current_user,
        db=db,
    )

    db.delete(score)
    db.commit()