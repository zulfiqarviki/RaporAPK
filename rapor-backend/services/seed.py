import os

from sqlalchemy.orm import Session

from core.security import hash_password
from models.user import User


def seed_default_admin(db: Session) -> None:
    admin_nip = os.getenv("DEFAULT_ADMIN_NIP", "admin")
    admin_name = os.getenv("DEFAULT_ADMIN_NAME", "Administrator")
    admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")

    existing_admin = db.query(User).filter(User.role == "admin").first()

    if existing_admin is not None:
        return

    admin = User(
        nip=admin_nip,
        name=admin_name,
        hashed_password=hash_password(admin_password),
        role="admin",
        is_active=True,
    )

    db.add(admin)
    db.commit()