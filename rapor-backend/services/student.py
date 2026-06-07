from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.student import Student
from models.user import User
from schemas.student import StudentCreate, StudentUpdate
from services.grade_table import get_grade_table_by_id


def list_students(
    grade_table_id: int,
    current_user: User,
    db: Session,
) -> list[Student]:
    grade_table = get_grade_table_by_id(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )

    return (
        db.query(Student)
        .filter(Student.grade_table_id == grade_table.id)
        .order_by(Student.id.asc())
        .all()
    )


def get_student_by_id(
    student_id: int,
    current_user: User,
    db: Session,
) -> Student:
    student = db.query(Student).filter(Student.id == student_id).first()

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

    return student


def create_student(
    grade_table_id: int,
    student_data: StudentCreate,
    current_user: User,
    db: Session,
) -> Student:
    grade_table = get_grade_table_by_id(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )

    student = Student(
        name=student_data.name,
        student_number=student_data.student_number,
        grade_table_id=grade_table.id,
    )

    db.add(student)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student number already exists in this grade table",
        )

    db.refresh(student)

    return student


def update_student(
    student_id: int,
    student_data: StudentUpdate,
    current_user: User,
    db: Session,
) -> Student:
    student = get_student_by_id(
        student_id=student_id,
        current_user=current_user,
        db=db,
    )

    if "name" in student_data.model_fields_set:
        student.name = student_data.name

    if "student_number" in student_data.model_fields_set:
        student.student_number = student_data.student_number

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student number already exists in this grade table",
        )

    db.refresh(student)

    return student


def delete_student(
    student_id: int,
    current_user: User,
    db: Session,
) -> None:
    student = get_student_by_id(
        student_id=student_id,
        current_user=current_user,
        db=db,
    )

    db.delete(student)
    db.commit()