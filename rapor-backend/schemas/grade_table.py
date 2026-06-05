from pydantic import BaseModel, ConfigDict

from .grade_component import GradeComponentOut
from .student import StudentOut


class GradeTableCreate(BaseModel):
    subject_name: str
    description: str | None = None


class GradeTableUpdate(BaseModel):
    subject_name: str | None = None
    description: str | None = None


class GradeTableOut(BaseModel):
    id: int
    subject_name: str
    description: str | None = None
    teacher_id: int
    components: list[GradeComponentOut] = []
    students: list[StudentOut] = []

    model_config = ConfigDict(from_attributes=True)