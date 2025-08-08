"""Main script"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.database import engine
from app.routers import tables, user, auth
from app.eis import routers as eis_routers

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Table routers
app.include_router(tables.company_router)
app.include_router(tables.person_router)
app.include_router(tables.location_router)
app.include_router(tables.job_router)
app.include_router(tables.job_application_router)
app.include_router(tables.aggregator_router)
app.include_router(tables.interview_router)
app.include_router(tables.keyword_router)
app.include_router(tables.file_router)
app.include_router(eis_routers.scrapedjob_router)
app.include_router(eis_routers.email_router)
app.include_router(eis_routers.servicelog_router)
app.include_router(tables.job_application_update_router)

# Authentification router
app.include_router(user.user_router)
app.include_router(auth.router)
