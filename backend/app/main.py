"""Main script"""

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.eis import routers as eis_routers
from app.routers import data_tables, user, login, export, settings

app = FastAPI()

print("=" * 80)
print("CORS MIDDLEWARE CONFIGURED - CUSTOM IMPLEMENTATION")
print("=" * 80)


class CORSHeaderMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware that FORCES headers on all responses"""

    async def dispatch(self, request: Request, call_next):
        # Handle OPTIONS requests immediately
        if request.method == "OPTIONS":
            return Response(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Max-Age": "3600",
                },
            )

        # Process the request
        response = await call_next(request)

        # Add CORS headers using mutable_headers
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT"
        response.headers["Access-Control-Allow-Headers"] = "*"

        return response


# Add the custom CORS middleware
app.add_middleware(CORSHeaderMiddleware)


# Exception handlers with CORS
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors and add CORS headers"""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions and add CORS headers"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
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

# Authentication router
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


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint"""
    return {"status": "ok"}
