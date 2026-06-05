from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class GradeComponent(Base):
    __tablename__ = "grade_components"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    grade_table_id = Column(Integer, ForeignKey("grade_tables.id"), nullable=False)

    grade_table = relationship("GradeTable", back_populates="components")
    scores = relationship("Score", back_populates="component", cascade="all, delete-orphan")
