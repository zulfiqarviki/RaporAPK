from pydantic import BaseModel, ConfigDict

class StudentCreate(BaseModel):
    name: str

class StudentOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
