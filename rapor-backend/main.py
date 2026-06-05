from fastapi import FastAPI

import models
from database.database import engine, Base, SessionLocal
from routers import auth
from services.seed import seed_default_admin

Base.metadata.create_all(bind=engine)


db = SessionLocal()
try:
    seed_default_admin(db)
finally:
    db.close()


app = FastAPI(
    title="Rapor API",
    description="Backend API for teacher grade management",
    version="0.1.0"
)

app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Rapor API is running"}
