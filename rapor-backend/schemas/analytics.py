from typing import Literal

from pydantic import BaseModel, Field, model_validator


class StudentFinalGradeOut(BaseModel):
    student_id: int
    student_name: str
    student_number: str | None = None
    final_grade: float
    is_complete: bool
    missing_components: list[str] = Field(default_factory=list)


class StudentComponentScoreOut(BaseModel):
    student_id: int
    student_name: str
    student_number: str | None = None
    score: float


class ComponentSummaryOut(BaseModel):
    component_id: int
    component_name: str
    weight: float
    order_index: int

    average_score: float
    highest_score: StudentComponentScoreOut | None = None
    lowest_score: StudentComponentScoreOut | None = None

    total_students: int
    filled_scores: int
    missing_scores: int


class AnalyticsSummaryOut(BaseModel):
    grade_table_id: int
    subject_name: str

    total_students: int
    total_components: int

    final_grade_average: float
    highest_final_grade: StudentFinalGradeOut | None = None
    lowest_final_grade: StudentFinalGradeOut | None = None

    component_summaries: list[ComponentSummaryOut]


class DistributionRange(BaseModel):
    label: str = Field(min_length=1)
    min: float = Field(ge=0, le=100)
    max: float = Field(ge=0, le=100)


class DistributionRequest(BaseModel):
    target: Literal["final_grade", "component"]
    component_id: int | None = None
    ranges: list[DistributionRange] = Field(min_length=1, max_length=10)

    @model_validator(mode="after")
    def validate_distribution_request(self):
        if self.target == "component" and self.component_id is None:
            raise ValueError("component_id is required when target is component")

        if self.target == "final_grade" and self.component_id is not None:
            raise ValueError("component_id must be null when target is final_grade")

        sorted_ranges = sorted(self.ranges, key=lambda item: item.min)

        labels = [item.label for item in sorted_ranges]
        if len(labels) != len(set(labels)):
            raise ValueError("Range labels must be unique")

        if sorted_ranges[0].min != 0:
            raise ValueError("First range must start from 0")

        if sorted_ranges[-1].max != 100:
            raise ValueError("Last range must end at 100")

        for index, current_range in enumerate(sorted_ranges):
            if current_range.min >= current_range.max:
                raise ValueError("Each range must have min lower than max")

            if index > 0:
                previous_range = sorted_ranges[index - 1]

                if abs(previous_range.max - current_range.min) > 1e-9:
                    raise ValueError("Ranges must be continuous and non-overlapping")

        self.ranges = sorted_ranges
        return self


class DistributionBucketOut(BaseModel):
    label: str
    min: float
    max: float
    count: int


class DistributionOut(BaseModel):
    grade_table_id: int
    subject_name: str

    target: Literal["final_grade", "component"]
    component_id: int | None = None
    component_name: str | None = None

    total_counted: int
    missing_count: int = 0

    distribution: list[DistributionBucketOut]


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
    missing_components: list[str] = Field(default_factory=list)


class StudentComparisonOut(BaseModel):
    grade_table_id: int
    subject_name: str
    comparison_type: str
    component_id: int | None = None
    component_name: str | None = None
    students: list[StudentComparisonItemOut]