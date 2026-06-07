from fastapi import FastAPI

import models
from database.database import engine, Base, SessionLocal
from services.seed import seed_default_admin
from routers import (
    auth,
    admin,
    grade_tables,
    grade_components,
    students,
    scores,
    results,
    analytics,
    excel
)
from fastapi.middleware.cors import CORSMiddleware

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


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(grade_tables.router)
app.include_router(grade_components.router)
app.include_router(students.router)
app.include_router(scores.router)
app.include_router(results.router)
app.include_router(analytics.router)
app.include_router(excel.router)


@app.get("/")
def root():
    return {"message": "Rapor API is running"}
