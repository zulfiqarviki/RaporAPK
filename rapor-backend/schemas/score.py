from pydantic import BaseModel, ConfigDict, Field


class ScoreCreate(BaseModel):
    student_id: int
    component_id: int
    score: float = Field(ge=0, le=100)


class ScoreUpdate(BaseModel):
    score: float | None = Field(default=None, ge=0, le=100)


class ScoreOut(BaseModel):
    id: int
    student_id: int
    component_id: int
    score: float

    model_config = ConfigDict(from_attributes=True)