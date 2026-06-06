from pydantic import BaseModel, Field


class ComponentAverageOut(BaseModel):
    component_id: int
    component_name: str
    weight: float
    order_index: int
    average_score: float
    total_students: int
    filled_scores: int
    missing_scores: int


class ComponentAveragesOut(BaseModel):
    grade_table_id: int
    subject_name: str
    component_averages: list[ComponentAverageOut]


class StudentProgressPointOut(BaseModel):
    component_id: int
    component_name: str
    weight: float
    order_index: int
    score: float | None = None


class StudentProgressOut(BaseModel):
    grade_table_id: int
    subject_name: str
    student_id: int
    student_name: str
    student_number: str | None = None
    progress: list[StudentProgressPointOut]


class StudentComparisonRequest(BaseModel):
    student_ids: list[int] = Field(min_length=2, max_length=5)
    component_id: int | None = None


class StudentComparisonItemOut(BaseModel):
    student_id: int
    student_name: str
    student_number: str | None = None
    value: float | None = None
    is_complete: bool | None = None
    missing_components: list[str] = []


class StudentComparisonOut(BaseModel):
    grade_table_id: int
    subject_name: str
    comparison_type: str
    component_id: int | None = None
    component_name: str | None = None
    students: list[StudentComparisonItemOut]