from pydantic import BaseModel
from typing import Optional
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, HTTPException, status
import secrets

class User(BaseModel):
    username: str
    disabled: bool = False

import os
from dotenv import load_dotenv
from pathlib import Path

# Charger les variables d'environnement
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

def load_users_from_env() -> dict:
    """
    Charge les utilisateurs depuis les variables d'environnement.
    Format attendu : 
    - ADMIN_USERNAME=admin
    - ADMIN_PASSWORD=hash_du_mot_de_passe
    - ADMIN_DISABLED=False
    """
    users = {}
    
    # Charger l'utilisateur admin
    admin_username = os.getenv('ADMIN_USERNAME')
    admin_password = os.getenv('ADMIN_PASSWORD')
    
    if admin_username and admin_password:
        users[admin_username] = {
            "username": admin_username,
            "password": admin_password,
            "disabled": os.getenv('ADMIN_DISABLED', 'False').lower() in ('true', '1', 't')
        }
    
    # Charger les utilisateurs supplémentaires (format: USER_USERNAME, USER_PASSWORD, USER_DISABLED)
    user_index = 1
    while True:
        username = os.getenv(f'USER{user_index}_USERNAME')
        if not username:
            break
            
        password = os.getenv(f'USER{user_index}_PASSWORD')
        if password:
            users[username] = {
                "username": username,
                "password": password,
                "disabled": os.getenv(f'USER{user_index}_DISABLED', 'False').lower() in ('true', '1', 't')
            }
        user_index += 1
    
    return users

# Charger les utilisateurs au démarrage
USERS_DB = load_users_from_env()

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
