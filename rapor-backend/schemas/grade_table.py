from pydantic import BaseModel, ConfigDict
from .grade_component import GradeComponentOut
from .student import StudentOut

class GradeTableCreate(BaseModel):
    name: str

class GradeTableOut(BaseModel):
    id: int
    name: str
    teacher_id: int
    components: list[GradeComponentOut] = []
    students: list[StudentOut] = []

    model_config = ConfigDict(from_attributes=True)
