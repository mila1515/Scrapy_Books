from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional

from books_api.domain.user import verify_credentials, User

# Schéma d'authentification Basic
security = HTTPBasic()

async def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Vérifie les identifiants de l'utilisateur via l'authentification Basic.
    """
    user = verify_credentials(credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    Vérifie que l'utilisateur est actif.
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Utilisateur inactif")
    return current_user
