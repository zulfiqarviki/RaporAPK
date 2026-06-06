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
    analytics
)


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
app.include_router(admin.router)
app.include_router(grade_tables.router)
app.include_router(grade_components.router)
app.include_router(students.router)
app.include_router(scores.router)
app.include_router(results.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    return {"message": "Rapor API is running"}
