# core/middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from jose import JWTError, jwt
from starlette.status import HTTP_401_UNAUTHORIZED
from typing import List, Optional
from datetime import datetime
from .config import settings

EXCLUDED_PATHS = [
    "/auth/login",
    "/auth/register",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/"
]

class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, excluded_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or EXCLUDED_PATHS

    async def dispatch(self, request: Request, call_next):
        # Kiểm tra path có trong danh sách excluded không
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authentication token"
            )

        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            
            # Lưu thông tin user vào request state
            request.state.user = payload.get("sub")
            request.state.user_data = payload

        except JWTError as e:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=f"Authentication error: {str(e)}"
            )

        return await call_next(request)