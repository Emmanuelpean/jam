"""Main script"""

import logging
import traceback

from fastapi import FastAPI, Request, Response, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app import config, models
from app.eis import routers as eis_routers
from app.routers import data_tables, user, login, export, settings
from app.database import get_db, SQLALCHEMY_DATABASE_URL, engine

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

        try:
            # Process the request
            response = await call_next(request)

            # Add CORS headers
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT"
            response.headers["Access-Control-Allow-Headers"] = "*"

            return response

        except Exception as e:
            # If anything crashes, return 500 with CORS headers
            print(f"❌ EXCEPTION IN MIDDLEWARE: {type(e).__name__}: {str(e)}")
            import traceback

            traceback.print_exc()

            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                },
            )


# Add the custom CORS middleware
app.add_middleware(CORSHeaderMiddleware)


# Global exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and add CORS headers"""
    print(f"❌ UNHANDLED EXCEPTION: {type(exc).__name__}: {str(exc)}")
    import traceback

    traceback.print_exc()

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )


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


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {exc}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return JSONResponse(status_code=500, content={"detail": f"Internal server error: {str(exc)}"})


@app.get("/health/db")
async def health_database(db: Session = Depends(get_db)):
    """Comprehensive database health check"""

    db_status = {"status": "unknown", "connection": {}, "configuration": {}, "tables": {}, "checks": {}}

    try:
        # Configuration info (hide sensitive parts)
        db_url_parts = SQLALCHEMY_DATABASE_URL.split("@")
        safe_url = db_url_parts[-1] if len(db_url_parts) > 1 else "unable to parse"

        db_status["configuration"] = {
            "database_name": config.settings.database_name,
            "database_hostname": config.settings.database_hostname,
            "database_port": config.settings.database_port,
            "url_safe": safe_url,
            "engine_pool_size": engine.pool.size() if hasattr(engine.pool, "size") else "N/A",
        }

        # Test 1: Connection established via dependency injection
        db_status["connection"]["established"] = True
        db_status["checks"]["dependency_injection"] = "✅ success"

        # Test 2: Simple query
        result = db.execute(text("SELECT 1")).scalar()
        db_status["checks"]["simple_query"] = "✅ success"
        db_status["checks"]["query_result"] = result

        # Test 3: Get all tables using inspector
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        db_status["tables"]["count"] = len(table_names)
        db_status["tables"]["names"] = table_names
        db_status["checks"]["tables_exist"] = "✅ yes" if table_names else "❌ no tables found"

        # Test 5: Check if we can get table columns
        if "users" in table_names:
            try:
                columns = inspector.get_columns("users")
                db_status["tables"]["users"]["columns"] = [col["name"] for col in columns]
            except Exception as e:
                db_status["tables"]["users"]["column_error"] = str(e)

        db_status["status"] = "healthy"

    except Exception as e:
        db_status["status"] = "unhealthy"
        db_status["error"] = {
            "message": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc().split("\n"),
        }

    return db_status
