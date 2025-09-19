from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse # Import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from app.core.config import settings
from app.core.database import init_db
from app.core.redis import close_redis_client
from app.api.v1.api import api_router
from sqlalchemy.exc import IntegrityError # Import IntegrityError
from fastapi.exceptions import RequestValidationError # Import RequestValidationError

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_redis_client()
    pass

app = FastAPI(
    title="Zidisha Loyalty Platform",
    description="Loyalty-as-a-Service platform for merchants using M-Pesa transactions",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False # Added this line to disable automatic trailing slash redirects
)

# Custom exception handler for RequestValidationError to catch Pydantic validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    # Inspect the errors to see if they originate from a unique constraint violation
    for error in exc.errors():
        if "duplicate key value violates unique constraint" in str(error.get("msg", "")) or \
           ("loc" in error and "mpesa_till_number" in error["loc"] and "already exists" in str(error.get("msg", ""))):
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={"detail": "Duplicate M-Pesa till number"}
            )
        elif ("loc" in error and "email" in error["loc"] and "already exists" in str(error.get("msg", ""))):
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={"detail": "Merchant with this email already exists."}
            )
    
    # If not a unique constraint violation, return a standard 422
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

# Custom exception handler for IntegrityError (e.g., unique constraint violations)
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc: IntegrityError):
    # Log the exception for debugging
    print(f"DEBUG: Caught IntegrityError: {str(exc)}")

    # Check for specific unique constraint violation messages
    if "duplicate key value violates unique constraint" in str(exc):
        detail = "Duplicate entry detected. Please ensure all unique fields are unique."
        if "ix_merchants_email" in str(exc):
            detail = "Merchant with this email already exists."
        elif "ix_merchants_mpesa_till_number" in str(exc):
            detail = "Merchant with this M-Pesa till number already exists."
        elif "ix_users_email" in str(exc):
            detail = "User with this email already exists."
        # Add more specific checks for other unique constraints as needed

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": detail}
        )
    # If it's an IntegrityError but not a duplicate key, re-raise as 500 or handle differently
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected database error occurred."}
    )

# Custom exception handler for HTTPException to ensure proper status codes are returned
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    print(f"DEBUG: Caught HTTPException: {exc.status_code} - {exc.detail}") # Debug print
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Zidisha Loyalty Platform API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True
    )