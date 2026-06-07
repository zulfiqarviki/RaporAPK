from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from database.database import Base


class Student(Base):
    __tablename__ = "students"

    __table_args__ = (
        UniqueConstraint(
            "grade_table_id",
            "student_number",
            name="unique_student_number_per_grade_table",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    student_number = Column(String, nullable=True)

    grade_table_id = Column(Integer, ForeignKey("grade_tables.id"), nullable=False)

    grade_table = relationship("GradeTable", back_populates="students")

    scores = relationship(
        "Score",
        back_populates="student",
        cascade="all, delete-orphan",
    )