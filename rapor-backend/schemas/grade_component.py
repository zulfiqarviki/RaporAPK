from pydantic import BaseModel, ConfigDict, Field


class GradeComponentCreate(BaseModel):
    name: str
    weight: float = Field(gt=0)
    order_index: int = 0


class GradeComponentUpdate(BaseModel):
    name: str | None = None
    weight: float | None = Field(default=None, gt=0)
    order_index: int | None = None


class GradeComponentOut(BaseModel):
    id: int
    name: str
    weight: float
    max_score: int
    order_index: int
    grade_table_id: int

    model_config = ConfigDict(from_attributes=True)