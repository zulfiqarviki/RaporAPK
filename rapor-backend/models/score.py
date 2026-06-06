from sqlalchemy import CheckConstraint, Column, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from database.database import Base


class Score(Base):
    __tablename__ = "scores"

    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="check_score_range"),
        UniqueConstraint(
            "student_id",
            "component_id",
            name="unique_score_per_student_component",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    score = Column(Float, nullable=False)

    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    component_id = Column(Integer, ForeignKey("grade_components.id"), nullable=False)

    student = relationship("Student", back_populates="scores")
    component = relationship("GradeComponent", back_populates="scores")