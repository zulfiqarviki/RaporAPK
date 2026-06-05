from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Float, nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    component_id = Column(Integer, ForeignKey("grade_components.id"), nullable=False)

    student = relationship("Student", back_populates="scores")
    component = relationship("GradeComponent", back_populates="scores")
