from pydantic import BaseModel, ConfigDict

class ScoreCreate(BaseModel):
    student_id: int
    component_id: int
    value: float

class ScoreOut(BaseModel):
    id: int
    student_id: int
    component_id: int
    value: float

    model_config = ConfigDict(from_attributes=True)

class FinalGradeOut(BaseModel):
    student_id: int
    student_name: str
    final_grade: float

    model_config = ConfigDict(from_attributes=True)
