from pydantic import BaseModel, ConfigDict


class StudentCreate(BaseModel):
    name: str
    student_number: str | None = None


class StudentUpdate(BaseModel):
    name: str | None = None
    student_number: str | None = None


class StudentOut(BaseModel):
    id: int
    name: str
    student_number: str | None = None
    grade_table_id: int

    model_config = ConfigDict(from_attributes=True)