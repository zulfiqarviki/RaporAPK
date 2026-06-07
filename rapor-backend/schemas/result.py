from pydantic import BaseModel


class ComponentScoreOut(BaseModel):
    component_id: int
    component_name: str
    weight: float
    score: float | None = None


class StudentResultOut(BaseModel):
    student_id: int
    student_name: str
    student_number: str | None = None
    component_scores: list[ComponentScoreOut]
    final_grade: float
    is_complete: bool
    missing_components: list[str]


class GradeTableResultOut(BaseModel):
    grade_table_id: int
    subject_name: str
    teacher_id: int
    teacher_name: str
    total_weight: float
    results: list[StudentResultOut]