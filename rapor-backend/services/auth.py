from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.security import create_access_token, verify_password
from models.user import User
from schemas.user import TokenOut


def login_user(nip: str, password: str, db: Session) -> TokenOut:
    user = db.query(User).filter(User.nip == nip).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid NIP or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid NIP or password",
        )

    access_token = create_access_token(
        data={
            "sub": user.nip,
            "role": user.role,
        }
    )

    return TokenOut(access_token=access_token)