from fastapi import FastAPI
from database.database import engine, Base
from models import *
from routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Rapor API",
    description="Backend API for teacher grade management",
    version="0.1.0"
)

app.include_router(auth.router)

@app.get("/")
def health_check():
    return {"message": "Rapor API is running"}
