# Books API

Cette API permet d'accéder aux données des livres extraites par le projet Scrapy.

## Configuration requise

- Python 3.7 ou supérieur
- Base de données SQLite (books.db) située dans le dossier `monprojet`

## Installation

1. Créez un environnement virtuel (recommandé) :
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Sur Windows
   source venv/bin/activate  # Sur macOS/Linux
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

L'API est déjà configurée pour utiliser la base de données SQLite située dans `monprojet/books.db`.

## Démarrage de l'API

```bash
uvicorn app.main:app --reload
```

L'API sera accessible à l'adresse : http://127.0.0.1:8000

## Documentation de l'API

Une fois l'API démarrée, vous pouvez accéder à la documentation interactive :
- Swagger UI : http://127.0.0.1:8000/docs
- ReDoc : http://127.0.0.1:8000/redoc

## Endpoints disponibles

- `GET /books/` - Liste tous les livres
- `GET /books/{book_id}` - Récupère un livre par son ID
- `GET /books/search/title/{title}` - Recherche des livres par titre
- `GET /books/category/{category}` - Recherche des livres par catégorie
- `GET /books/stats/` - Affiche des statistiques sur les livres

## Tests

Pour exécuter les tests :

```bash
pytest
```
