"""
Module d'authentification simplifiée pour l'API.

Fournit une authentification HTTP Basic simple pour sécuriser les endpoints de l'API.
"""

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

# Configuration de l'authentification HTTP Basic
security = HTTPBasic()

# Création du routeur
router = APIRouter(
    prefix="/api/auth",
    tags=["Authentification"]
)

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> bool:
    """
    Vérifie les identifiants de l'utilisateur.
    
    Args:
        credentials: Les identifiants fournis par l'utilisateur
        
    Returns:
        bool: True si les identifiants sont valides
        
    Raises:
        HTTPException: Si les identifiants sont invalides
    """
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "admin123")
    
    if not (correct_username and correct_password):
        logger.warning(f"Tentative de connexion échouée pour l'utilisateur: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True
