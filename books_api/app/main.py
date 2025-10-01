from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.presentation.routes import books
from app.core.config import SQLITE_PATH
import os
import logging
import sys

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

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
    version="1.0.0",
    docs_url=None,  # Désactive la doc par défaut pour la personnaliser
    redoc_url=None
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, remplacer par les origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(books.router)

# Vérifier que la base de données existe
if not os.path.exists(SQLITE_PATH):
    logging.error(f"La base de données n'existe pas à l'emplacement : {SQLITE_PATH}")
    logging.info("Veuillez exécuter le spider Scrapy pour créer la base de données.")

# Routes personnalisées pour la documentation
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Books API - Documentation",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Gestion des erreurs globales
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logging.error(f"Erreur non gérée: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Une erreur interne est survenue"},
    )

# Route de santé
@app.get("/health", include_in_schema=False)
async def health_check():
    """
    Vérifie que l'API est opérationnelle
    """
    return {"status": "ok", "message": "API en cours d'exécution"}

# Message de démarrage
@app.on_event("startup")
async def startup_event():
    logging.info("Démarrage de l'API Books...")
    try:
        if os.path.exists(SQLITE_PATH):
            logging.info(f"Base de données trouvée : {SQLITE_PATH}")
        else:
            logging.warning(f"Base de données introuvable : {SQLITE_PATH}")
            logging.info("✅ Base de données initialisée")
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'initialisation: {e}")
        raise

# Configuration pour le redémarrage automatique en développement
if os.environ.get("ENV") == "development":
    import uvicorn
    
    @app.on_event("shutdown")
    async def shutdown_event():
        logging.info("Arrêt de l'application...")
    
    if __name__ == "__main__":
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
