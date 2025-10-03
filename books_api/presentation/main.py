from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from fastapi.staticfiles import StaticFiles
import logging
import sys
import uvicorn
from typing import List

from books_api.data.config import API_CONFIG, CORS_CONFIG
from books_api.data.book_repository import BookRepository
from books_api.domain.book_usecases import BookUseCases
from books_api.domain.user import User, verify_credentials

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log', mode='a', encoding='utf-8')
    ]
)

# Création de l'application FastAPI avec la configuration
app = FastAPI(**API_CONFIG)

# Configuration CORS
app.add_middleware(CORSMiddleware, **CORS_CONFIG)

# Dépendances
def get_book_usecases():
    """Retourne une instance de BookUseCases configurée avec le repository."""
    repo = BookRepository()
    # Ne pas créer les tables automatiquement car on utilise une base existante
    logger.info(f"Utilisation de la base de données: {repo.db_path}")
    return BookUseCases(repo)

# Gestionnaire d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Erreur non gérée: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Une erreur interne est survenue"},
    )

# Route de santé
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "L'API est opérationnelle"}

# Route protégée pour tester l'authentification
@app.get("/users/me/")
async def read_users_me(user: User = Depends(verify_credentials)):
    return {"username": user.username}

# Inclure les routes d'API
from books_api.presentation import routes  # Importation absolue des routes

# Inclure le routeur des livres
app.include_router(routes.router)

# Point d'entrée pour l'exécution directe
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
