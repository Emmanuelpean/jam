"""Main script"""

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.routers import data_tables, user, auth, export, settings
from app.eis import routers as eis_routers
from app import models
from app.database import engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data table routers
app.include_router(data_tables.company_router)
app.include_router(data_tables.person_router)
app.include_router(data_tables.location_router)
app.include_router(data_tables.job_router)
app.include_router(data_tables.aggregator_router)
app.include_router(data_tables.interview_router)
app.include_router(data_tables.keyword_router)
app.include_router(data_tables.file_router)
app.include_router(data_tables.job_application_update_router)

# EIS routers
app.include_router(eis_routers.scrapedjob_router)
app.include_router(eis_routers.email_router)
app.include_router(eis_routers.eis_servicelog_router)
app.include_router(eis_routers.scraper_router)

# Authentification router
app.include_router(user.user_router)
app.include_router(user.current_user_router)
app.include_router(auth.login_router)
app.include_router(auth.register_router)
app.include_router(auth.password_router)

# Export router
app.include_router(export.router)

# Settings router
app.include_router(settings.settings_router)


@app.get("/")
def read_root() -> dict:
    """Root endpoint"""

    return {"message": "Welcome to the JAM API"}


health_router = APIRouter(prefix="/health", tags=["health"])


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint"""

    return {"status": "ok"}
