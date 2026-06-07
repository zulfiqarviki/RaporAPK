from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.security import hash_password
from models.user import User
from schemas.user import TeacherCreate, TeacherUpdate


def get_all_teachers(db: Session) -> list[User]:
    return db.query(User).filter(User.role == "teacher").all()


def create_teacher(user_data: TeacherCreate, db: Session) -> User:
    existing_user = db.query(User).filter(User.nip == user_data.nip).first()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="NIP already registered",
        )

    teacher = User(
        nip=user_data.nip,
        name=user_data.name,
        hashed_password=hash_password(user_data.password),
        role="teacher",
        is_active=True,
    )

    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    return teacher


def update_teacher(teacher_id: int, user_data: TeacherUpdate, db: Session) -> User:
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

    if user_data.nip is not None and user_data.nip != teacher.nip:
        existing_user = db.query(User).filter(User.nip == user_data.nip).first()

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="NIP already registered",
            )

        teacher.nip = user_data.nip

    if user_data.name is not None:
        teacher.name = user_data.name

    if user_data.password is not None:
        teacher.hashed_password = hash_password(user_data.password)

    if user_data.is_active is not None:
        teacher.is_active = user_data.is_active

    db.commit()
    db.refresh(teacher)

    return teacher


def delete_teacher(teacher_id: int, db: Session) -> None:
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

    db.delete(teacher)
    db.commit()