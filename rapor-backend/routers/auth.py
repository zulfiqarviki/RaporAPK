from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.database import get_db
from schemas.teacher import TeacherCreate, TeacherOut, TokenOut, LoginRequest
from services.auth import register_teacher, login_teacher

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=TeacherOut, status_code=status.HTTP_201_CREATED)
def register(teacher: TeacherCreate, db: Session = Depends(get_db)):
    return register_teacher(data=teacher, db=db)

@router.post("/login", response_model=TokenOut, status_code=status.HTTP_200_OK)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return login_teacher(nip=data.nip, password=data.password, db=db)
