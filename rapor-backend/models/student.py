from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    grade_table_id = Column(Integer, ForeignKey("grade_tables.id"), nullable=False)

    grade_table = relationship("GradeTable", back_populates="students")
    scores = relationship("Score", back_populates="student", cascade="all, delete-orphan")
