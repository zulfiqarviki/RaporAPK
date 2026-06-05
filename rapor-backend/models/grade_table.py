from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.database import Base


class GradeTable(Base):
    __tablename__ = "grade_tables"

    id = Column(Integer, primary_key=True, index=True)

    subject_name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    teacher = relationship("User", back_populates="grade_tables")

    components = relationship(
        "GradeComponent",
        back_populates="grade_table",
        cascade="all, delete-orphan",
    )

    students = relationship(
        "Student",
        back_populates="grade_table",
        cascade="all, delete-orphan",
    )