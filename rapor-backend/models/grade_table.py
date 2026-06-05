from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class GradeTable(Base):
    __tablename__ = "grade_tables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)

    teacher = relationship("Teacher", back_populates="grade_tables")
    components = relationship("GradeComponent", back_populates="grade_table", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="grade_table", cascade="all, delete-orphan")
