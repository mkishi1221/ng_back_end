from fastapi import Depends, Response, status
from fastapi.security import HTTPBearer
from .utils import VerifyToken

token_auth_scheme = HTTPBearer()

async def require_auth_token(token: str = Depends(token_auth_scheme)):
    result = VerifyToken(token.credentials).verify()
    if result.get("status"):
        return Response(result, status_code=status.HTTP_401_UNAUTHORIZED)