from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.teacher import Teacher
from schemas.teacher import TeacherCreate, TokenOut
from core.security import hash_password, verify_password, create_access_token

def register_teacher(data: TeacherCreate, db: Session) -> Teacher:
    existing_teacher = db.query(Teacher).filter(Teacher.nip == data.nip).first()
    if existing_teacher:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="NIP already registered")
        
    hashed_pwd = hash_password(data.password)
    new_teacher = Teacher(nip=data.nip, name=data.name, hashed_password=hashed_pwd)
    
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    
    return new_teacher

def login_teacher(nip: str, password: str, db: Session) -> TokenOut:
    teacher = db.query(Teacher).filter(Teacher.nip == nip).first()
    if not teacher:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
    if not verify_password(password, teacher.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
    token = create_access_token(data={"sub": teacher.nip})
    return TokenOut(access_token=token)
