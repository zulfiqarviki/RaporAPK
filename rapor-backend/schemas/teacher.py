from pydantic import BaseModel, ConfigDict

class TeacherCreate(BaseModel):
    nip: str
    name: str
    password: str


class LoginRequest(BaseModel):
    nip: str
    password: str
    
class TeacherOut(BaseModel):
    id: int
    nip: str
    name: str

    model_config = ConfigDict(from_attributes=True)

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
