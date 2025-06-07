"""Main script"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import tables, user, auth
from app import models
from app.database import engine


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Table routers
app.include_router(tables.company_router)
app.include_router(tables.person_router)
app.include_router(tables.location_router)
app.include_router(tables.job_router)
# app.include_router(tables.jobapplication_router)
app.include_router(tables.aggregator_router)
# app.include_router(tables.interview_router)
app.include_router(tables.keyword_router)

# Authentification router
app.include_router(user.user_router)
app.include_router(auth.router)


@app.get("/")
def main() -> dict:
    """main page"""

    return {"message": "Welcome to the API. Hello World!!!"}
