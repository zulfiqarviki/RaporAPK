from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database.database import get_db
from models.user import Teacher
from core.security import decode_token
from typing import Optional

def get_current_teacher(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Teacher:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if authorization is None or not authorization.startswith("Bearer "):
        raise credentials_exception

    token = authorization.split(" ")[1]

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    nip: str = payload.get("sub")
    if nip is None:
        raise credentials_exception

    teacher = db.query(Teacher).filter(Teacher.nip == nip).first()
    if teacher is None:
        raise credentials_exception

    return teacher
