if __name__ == "__main__":
    import uvicorn
    import os
    import multiprocessing
    from dotenv import load_dotenv
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # Configuration du serveur
    HOST = os.getenv("API_HOST", "127.0.0.1")
    PORT = int(os.getenv("API_PORT", 8000))
    
    # Détecter si on est en développement
    ENV = os.getenv("ENV", "development").lower()
    IS_DEV = ENV in ["dev", "development"]
    
    # Configuration des workers
    WORKERS = 1 if IS_DEV else min(multiprocessing.cpu_count() * 2 + 1, 4)
    
    # Configuration du logging
    LOG_LEVEL = "debug" if IS_DEV else "info"
    
    # Afficher les informations de démarrage
    print("\n" + "=" * 50)
    print(f"Démarrage de l'API en mode {'DÉVELOPPEMENT' if IS_DEV else 'PRODUCTION'}")
    print("=" * 50)
    print(f"Hôte: {HOST}")
    print(f"Port: {PORT}")
    print(f"Workers: {WORKERS}")
    print(f"Niveau de log: {LOG_LEVEL.upper()}")
    print("\nDocumentation de l'API:")
    print(f"- Swagger UI: http://{HOST}:{PORT}/docs")
    print(f"- ReDoc: http://{HOST}:{PORT}/redoc")
    print("\nAppuyez sur Ctrl+C pour arrêter le serveur\n")
    
    # Configuration Uvicorn
    config = uvicorn.Config(
        app="books_api.presentation.main:app",
        host=HOST,
        port=PORT,
        workers=WORKERS,
        log_level=LOG_LEVEL,
        access_log=True,
        # Optimisations de performance
        limit_concurrency=1000,  # Augmenter la limite de connexions simultanées
        backlog=4096,  # Augmenter la file d'attente des connexions
        timeout_keep_alive=30,  # Timeout de 30 secondes pour les connexions inactives
        http="auto",  # Choisir automatiquement entre httptools et h11
        loop="auto",  # Choisir automatiquement la boucle d'événements
        ws="auto",  # Choisir automatiquement l'implémentation WebSocket
        reload=IS_DEV,  # Rechargement automatique uniquement en développement
        reload_dirs=["books_api"] if IS_DEV else None,  # Dossiers à surveiller pour le rechargement
        reload_delay=1.0,  # Délai avant rechargement après détection de changement
        reload_includes=["*.py"],  # Fichiers à surveiller pour le rechargement
        reload_excludes=["*.pyc"],  # Fichiers à ignorer pour le rechargement
        # Désactiver les fonctionnalités inutiles
        proxy_headers=False,  # Désactiver le support des en-têtes de proxy
        server_header=True,  # Activer l'en-tête Server
        date_header=True,  # Activer l'en-tête Date
        forwarded_allow_ips=None,  # Désactiver le support des en-têtes X-Forwarded-*
        # Configuration des logs
        log_config=None,  # Utiliser la configuration de logging par défaut
        use_colors=True,  # Activer les couleurs dans les logs
    )
    
    # Démarrer le serveur
    server = uvicorn.Server(config)
    server.run()
