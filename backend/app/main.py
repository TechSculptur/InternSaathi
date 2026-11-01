from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.routes import health_router, options_router, internships_router, recommendations_router, resume_router

# Configure basic logger without logging user profiles or sensitive data
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("internship_saathi")

app = FastAPI(
    title="Internship Saathi API",
    description=(
        "Lightweight demonstration internship recommendation prototype inspired by the "
        "PM Internship Scheme problem statement. Not an official government portal. "
        "Demonstration sample data only."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global safe exception handler: never leak raw stack traces to client
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Internal server error on path {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred while processing your request. Please try again.",
            "type": "InternalServerError"
        }
    )

# Include API v1 Routers
app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(options_router, prefix="/api/v1", tags=["Options"])
app.include_router(internships_router, prefix="/api/v1", tags=["Internships"])
app.include_router(recommendations_router, prefix="/api/v1", tags=["Recommendations"])
app.include_router(resume_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to Internship Saathi API",
        "docs": "/docs",
        "health": "/api/v1/health",
        "disclaimer": "Demonstration prototype. Sample internships only. Not an official government portal."
    }
