from sqlalchemy import CheckConstraint, Column, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from database.database import Base


class GradeComponent(Base):
    __tablename__ = "grade_components"

    __table_args__ = (
        CheckConstraint("weight > 0", name="check_component_weight_positive"),
        CheckConstraint("max_score = 100", name="check_component_max_score_100"),
        UniqueConstraint(
            "grade_table_id",
            "name",
            name="unique_component_name_per_grade_table",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    max_score = Column(Integer, nullable=False, default=100)
    order_index = Column(Integer, nullable=False, default=0)

    grade_table_id = Column(Integer, ForeignKey("grade_tables.id"), nullable=False)

    grade_table = relationship("GradeTable", back_populates="components")

    scores = relationship(
        "Score",
        back_populates="component",
        cascade="all, delete-orphan",
    )