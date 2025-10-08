"""Main script"""

from fastapi import FastAPI, APIRouter, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.routers import data_tables, user, login, export, settings
from app.eis import routers as eis_routers

app = FastAPI()

# CRITICAL: Add CORS middleware FIRST, before any other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Add this
)


# Debug middleware to log CORS issues
@app.middleware("http")
async def debug_cors(request: Request, call_next):
    """Debug CORS issues"""

    # Log incoming request
    if request.method == "OPTIONS":
        print(f"\n🔍 CORS Preflight Request to: {request.url.path}")
        print(f"   Origin: {request.headers.get('origin', 'None')}")
        print(f"   Method: {request.headers.get('access-control-request-method', 'None')}")

    response = await call_next(request)

    # Log CORS headers in response
    if request.method == "OPTIONS":
        print(f"📤 CORS Preflight Response:")
        print(f"   Status: {response.status_code}")
        print(f"   Access-Control-Allow-Origin: {response.headers.get('access-control-allow-origin', 'MISSING!')}")
        print(f"   Access-Control-Allow-Methods: {response.headers.get('access-control-allow-methods', 'MISSING!')}")
        print(f"   Access-Control-Allow-Headers: {response.headers.get('access-control-allow-headers', 'MISSING!')}\n")

    return response


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
app.include_router(login.router)

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


# Print immediately after adding middleware
import sys

print("=" * 80, file=sys.stderr)
print("CORS MIDDLEWARE CONFIGURED", file=sys.stderr)
print("=" * 80, file=sys.stderr)
print("allow_origins: ['*']", file=sys.stderr)
print("allow_credentials: False", file=sys.stderr)
print("=" * 80, file=sys.stderr)
