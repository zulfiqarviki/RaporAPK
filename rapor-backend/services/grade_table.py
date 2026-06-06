from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.grade_table import GradeTable
from models.user import User
from schemas.grade_table import GradeTableCreate, GradeTableUpdate


def get_teacher_or_404(teacher_id: int, db: Session) -> User:
    teacher = (
        db.query(User)
        .filter(User.id == teacher_id, User.role == "teacher")
        .first()
    )

    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found",
        )

    return teacher


def list_grade_tables(
    current_user: User,
    db: Session,
) -> list[GradeTable]:
    if current_user.role == "admin":
        return db.query(GradeTable).all()

    return (
        db.query(GradeTable)
        .filter(GradeTable.teacher_id == current_user.id)
        .all()
    )


def get_grade_table_by_id(
    grade_table_id: int,
    current_user: User,
    db: Session,
) -> GradeTable:
    grade_table = (
        db.query(GradeTable)
        .filter(GradeTable.id == grade_table_id)
        .first()
    )

    if grade_table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade table not found",
        )

    if current_user.role == "admin":
        return grade_table

    if grade_table.teacher_id == current_user.id:
        return grade_table

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have access to this grade table",
    )


def create_grade_table(
    grade_table_data: GradeTableCreate,
    current_user: User,
    db: Session,
) -> GradeTable:
    if current_user.role == "admin":
        if grade_table_data.teacher_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="teacher_id is required when admin creates a grade table",
            )

        get_teacher_or_404(grade_table_data.teacher_id, db)
        owner_id = grade_table_data.teacher_id

    else:
        if grade_table_data.teacher_id is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teacher cannot assign grade table owner",
            )

        owner_id = current_user.id

    grade_table = GradeTable(
        subject_name=grade_table_data.subject_name,
        description=grade_table_data.description,
        teacher_id=owner_id,
    )

    db.add(grade_table)
    db.commit()
    db.refresh(grade_table)

    return grade_table


def update_grade_table(
    grade_table_id: int,
    grade_table_data: GradeTableUpdate,
    current_user: User,
    db: Session,
) -> GradeTable:
    grade_table = get_grade_table_by_id(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )

    if grade_table_data.subject_name is not None:
        grade_table.subject_name = grade_table_data.subject_name

    if grade_table_data.description is not None:
        grade_table.description = grade_table_data.description

    db.commit()
    db.refresh(grade_table)

    return grade_table


def delete_grade_table(
    grade_table_id: int,
    current_user: User,
    db: Session,
) -> None:
    grade_table = get_grade_table_by_id(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )

    db.delete(grade_table)
    db.commit()