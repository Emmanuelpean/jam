"""Main script"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import job, user, location, company, aggregator, auth, person
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


# Include the routers
app.include_router(job.router)
app.include_router(location.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(company.router)
app.include_router(person.router)
app.include_router(aggregator.router)


@app.get("/")
def main() -> dict:
    """main page"""

    return {"message": "Welcome to the API. Hello World!!!"}
