"""
Point d'entrée principal de l'API FastAPI.

Ce module configure et initialise l'application FastAPI avec :
- Configuration CORS pour le développement
- Documentation interactive (Swagger et ReDoc)
- Gestion des erreurs
- Routes d'API
"""

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import des routeurs
from app.presentation.books_routes import router as books_router
from app.presentation.auth_routes import router as auth_router
from app.presentation.analytics_routes import router as analytics_router

# Création de l'application FastAPI
app = FastAPI(
    title="API de Gestion de Livres",
    description="API pour accéder aux données des livres scrapés",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS (à restreindre en production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routeurs
app.include_router(books_router)
app.include_router(auth_router)
app.include_router(analytics_router)

# Route de test
@app.get("/")
async def root():
    """Route de test pour vérifier que l'API fonctionne."""
    return {
        "message": "API de gestion de livres en cours d'exécution",
        "documentation": "/docs ou /redoc"
    }

# Gestionnaire d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Erreur non gérée: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Une erreur inattendue s'est produite"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
