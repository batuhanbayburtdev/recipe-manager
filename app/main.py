from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.database import engine, Base
from app.api import endpoints

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Recipe Manager API",
    description="A clean-architecture FastAPI backend for managing recipes.",
    version="1.0.0",
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(endpoints.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Recipe API! Go to /docs to see the interface."}