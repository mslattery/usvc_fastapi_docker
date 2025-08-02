import os
from fastapi import Request, Depends, HTTPException
from jose import jwt, JWTError
from starlette.status import HTTP_401_UNAUTHORIZED

# This secret key must be the same as the one in main.py
SECRET_KEY = os.environ.get('SECRET_KEY', 'a_very_secret_key_for_sure_man')

async def get_current_user(request: Request):
    """
    Dependency to get the current user from the session cookie.
    Raises an exception if the user is not authenticated.
    """
    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated"
        )
    
    # The token from the cookie is in the format "Bearer <token>"
    token = token.split("Bearer ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, 
            detail="Invalid token"
        )