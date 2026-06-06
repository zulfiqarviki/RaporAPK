from pydantic import BaseModel, ConfigDict


class GradeTableCreate(BaseModel):
    subject_name: str
    description: str | None = None
    teacher_id: int | None = None


class GradeTableUpdate(BaseModel):
    subject_name: str | None = None
    description: str | None = None


class GradeTableOut(BaseModel):
    id: int
    subject_name: str
    description: str | None = None
    teacher_id: int

    model_config = ConfigDict(from_attributes=True)