from pydantic import BaseModel, ConfigDict

class GradeComponentCreate(BaseModel):
    name: str
    weight: float

class GradeComponentOut(BaseModel):
    id: int
    name: str
    weight: float

    model_config = ConfigDict(from_attributes=True)
