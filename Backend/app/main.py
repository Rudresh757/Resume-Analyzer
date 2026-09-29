import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database import init_db
from app.routes.auth import router as auth_router
from app.routes.interview import router as interview_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("app.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager for startup and shutdown events.
    """
    logger.info("Initializing Resume AI FastAPI Backend...")
    try:
        init_db()
        logger.info("Connected to MySQL and initialized database schema.")
    except Exception as e:
        logger.error(
            f"Database initialization failed: {e}\n"
            f"Please verify MySQL Workbench is running and check settings in Backend/.env"
        )
    yield
    logger.info("Shutting down Resume AI Backend...")

app = FastAPI(
    title="Resume AI API",
    description="FastAPI Backend for Resume Analysis & Interview Preparation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Exception Handlers to match Node/Express response structure {"message": "..."}
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, (dict, list)):
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(status_code=exc.status_code, content={"message": str(detail)})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    msg = first_error.get("msg", "Invalid request parameters")
    field = " -> ".join([str(loc) for loc in first_error.get("loc", [])])
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": f"Validation error at {field}: {msg}"}
    )

# Register API Routers
app.include_router(auth_router)
app.include_router(interview_router)

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Resume AI Backend",
        "framework": "FastAPI + Uvicorn + SQLAlchemy",
        "database": "MySQL"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}
