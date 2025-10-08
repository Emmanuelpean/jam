"""Main script"""

from fastapi import APIRouter
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.eis import routers as eis_routers
from app.routers import data_tables, user, login, export, settings

app = FastAPI()


# Custom middleware to FORCE CORS headers on everything
@app.middleware("http")
async def force_cors_headers(request: Request, call_next):
    """Force CORS headers on ALL responses"""

    # Handle OPTIONS requests immediately
    if request.method == "OPTIONS":
        return JSONResponse(
            content={},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Max-Age": "3600",
            },
        )

    # Process the request
    response = await call_next(request)

    # FORCE CORS headers on the response
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT"
    response.headers["Access-Control-Allow-Headers"] = "*"

    return response


# CRITICAL: Add CORS middleware FIRST, before any other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Add this
)


# Add CORS headers to validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors and add CORS headers"""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT",
            "Access-Control-Allow-Headers": "*",
        },
    )


# Add CORS headers to HTTP exceptions
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions and add CORS headers"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT",
            "Access-Control-Allow-Headers": "*",
        },
    )


# Debug middleware
@app.middleware("http")
async def debug_cors(request: Request, call_next):
    """Debug CORS issues"""

    if request.method == "OPTIONS":
        print(f"\n🔍 CORS Preflight Request to: {request.url.path}")
        print(f"   Origin: {request.headers.get('origin', 'None')}")

    response = await call_next(request)

    # Log all responses
    print(f"📤 Response to {request.method} {request.url.path}:")
    print(f"   Status: {response.status_code}")
    print(f"   CORS Header: {response.headers.get('access-control-allow-origin', 'MISSING!')}")

    return response


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

print("=" * 80)
print("CORS MIDDLEWARE CONFIGURED")
print("=" * 80)
print("allow_origins: ['*']")
print("allow_credentials: False")
print("=" * 80)
