from pydantic import BaseModel
from typing import Optional
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, HTTPException, status
import secrets

class User(BaseModel):
    username: str
    disabled: bool = False

# Utilisateur par défaut
USERS_DB = {
    "admin": {
        "username": "admin",
        "password": "admin123",  # En production, utilisez un hachage sécurisé
        "disabled": False
    }
}

def verify_credentials(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    """
    Vérifie les identifiants de l'utilisateur.
    
    Args:
        credentials: Les identifiants de l'utilisateur (username/password)
        
    Returns:
        User: L'utilisateur authentifié
        
    Raises:
        HTTPException: Si les identifiants sont invalides
    """
    user_data = USERS_DB.get(credentials.username)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # En production, utilisez une vérification de mot de passe haché
    if not secrets.compare_digest(credentials.password, user_data["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return User(username=user_data["username"], disabled=user_data["disabled"])
