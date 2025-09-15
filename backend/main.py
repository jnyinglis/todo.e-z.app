from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from app.core.database import create_tables
from app.api import auth, users, health, build_info, seo
from app.core.security_config import apply_security_middleware, validate_security_config
from app.core.logging_config import (
    setup_logging,
    RequestLoggingMiddleware,
    APIError,
    api_error_handler,
    http_exception_handler,
    general_exception_handler,
    app_logger
)
from app.core.config import settings
from app.schemas.response import MessageResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    # Setup logging first
    setup_logging()
    app_logger.info("Application starting up")

    # Validate security configuration
    security_issues = validate_security_config()
    if security_issues and settings.environment == "production":
        app_logger.error("Security configuration issues found:")
        for issue in security_issues:
            app_logger.error(f"  - {issue}")
        # In production, you might want to exit here
        # raise Exception("Security configuration validation failed")
    elif security_issues:
        app_logger.warning("Security configuration warnings:")
        for issue in security_issues:
            app_logger.warning(f"  - {issue}")

    app_logger.info(f"Application started in {settings.environment} mode")

    # Note: Tables are now managed by Alembic migrations
    # await create_tables()  # Disabled in favor of migrations
    yield

    # Shutdown
    app_logger.info("Application shutting down")


app = FastAPI(
    title="Vite React FastAPI Template",
    description="Full-stack template with authentication",
    version="1.0.0",
    lifespan=lifespan,
)

# Apply security middleware (includes CORS, security headers, rate limiting, etc.)
app = apply_security_middleware(app)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add error handlers
app.add_exception_handler(APIError, api_error_handler)  # type: ignore[arg-type]
app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(build_info.router, prefix="/api", tags=["build-info"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(seo.router, tags=["seo"])


@app.get("/", response_model=MessageResponse)
async def root() -> MessageResponse:
    return MessageResponse(message="Vite React FastAPI Template API")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)