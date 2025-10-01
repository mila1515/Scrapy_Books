from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

from app.presentation.routes import books
from app.data.config.config import SQLITE_PATH
import os
import logging
import sys

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log', mode='a', encoding='utf-8')
    ]
)

# Définir le niveau de log pour sqlite3
logging.getLogger('sqlite3').setLevel(logging.DEBUG)

# Création de l'application FastAPI
app = FastAPI(
    title="Books API",
    description="""
    API pour accéder aux données des livres extraites par le projet Scrapy.
    
    Cette API permet de :
    - Lister tous les livres
    - Rechercher des livres par titre ou catégorie
    - Obtenir des statistiques sur les livres
    """,
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(books.router, prefix="/api")

# Gestion des erreurs globales
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Erreur non gérée: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Une erreur interne est survenue"}
    )

# Route de santé
@app.get("/health", tags=["santé"])
async def health_check():
    return {"status": "ok", "message": "API en cours d'exécution"}

# Vérification de la base de données au démarrage
@app.on_event("startup")
async def startup_event():
    logging.info("Démarrage de l'API Books...")
    if os.path.exists(SQLITE_PATH):
        logging.info(f"Base de données trouvée : {SQLITE_PATH}")
    else:
        logging.warning(f"Base de données introuvable : {SQLITE_PATH}")

# Configuration pour le redémarrage automatique en développement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
