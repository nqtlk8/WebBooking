from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from api import auth, seat, ticket_type, booking
from database import engine, Base
from core.middleware import JWTMiddleware
import logging
from core.config import settings
from database import get_db
from models.user import User
from schemas.user import UserCreate, UserResponse, Token, TokenData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Configure OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

app = FastAPI(
    title="Movie Booking API",
    description="API for movie booking system",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI endpoint
    redoc_url="/redoc",  # ReDoc endpoint
    openapi_url="/openapi.json",  # OpenAPI schema endpoint
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "useBasicAuthenticationWithAccessCodeGrant": True
    }
)

# Thêm CORS middleware với cấu hình cho phép tất cả
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Add JWT Middleware with excluded paths
app.add_middleware(
    JWTMiddleware,
    excluded_paths=[
        "/docs",
        "/redoc",
        "/openapi.json",
        "/auth/login",
        "/auth/register",
        "/"
    ]
)

# Thêm middleware để log requests
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {request.headers}")
    response = await call_next(request)
    logger.info(f"Response headers: {response.headers}")
    return response

# Include routers with proper prefixes and tags
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}}
)

# Add booking router
app.include_router(
    booking.router,
    prefix="/bookings",
    tags=["Bookings"],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        500: {"description": "Internal server error"}
    }
)

app.include_router(
    seat.router,
    prefix="/seats",
    tags=["Seats"],
    responses={404: {"description": "Not found"}}
)

app.include_router(
    ticket_type.router,
    prefix="/ticket-types",
    tags=["Ticket Types"],
    responses={404: {"description": "Not found"}}
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Movie Booking API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 