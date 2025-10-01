# 📚 Books API

API RESTful pour accéder aux données des livres extraites par le projet Scrapy. Cette API est optimisée pour fonctionner avec une base de données SQLite existante.

## 🚀 Fonctionnalités

- Accès aux données des livres via une API REST
- Recherche par titre et par catégorie
- Statistiques sur le catalogue de livres
- Documentation interactive (Swagger UI et ReDoc)
- Compatible avec la base de données SQLite existante

## 📋 Prérequis

- Python 3.8 ou supérieur
- Base de données SQLite (`monprojet/books.db`)
- Gestionnaire de paquets pip

## 🛠️ Installation

1. **Cloner le dépôt** (si ce n'est pas déjà fait)
   ```bash
   git clone [URL_DU_REPO]
   cd books_api
   ```

2. **Créer un environnement virtuel** (recommandé)
   ```bash
   # Sur Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Sur macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

L'API est configurée pour utiliser automatiquement la base de données SQLite située dans :
```
monprojet/books.db
```

## 🚀 Lancement

```bash
uvicorn app.main:app --reload
```

L'API sera accessible à : http://127.0.0.1:8000

## 📚 Documentation de l'API

Une fois l'API démarrée, accédez à la documentation :

- **Swagger UI** (interactif) : http://127.0.0.1:8000/docs
- **ReDoc** (documentation) : http://127.0.0.1:8000/redoc

## 🔍 Endpoints disponibles

### Livres
- `GET /books/` - Liste tous les livres
- `GET /books/{book_id}` - Détails d'un livre spécifique

### Recherche
- `GET /books/search/title/{title}` - Recherche par titre
- `GET /books/category/{category}` - Recherche par catégorie

### Statistiques
- `GET /books/stats/` - Statistiques sur le catalogue

## 🧪 Tests

Pour lancer les tests :

```bash
pytest
```

## 📦 Dépendances principales

- **FastAPI** - Framework web moderne et rapide
- **SQLite3** - Base de données embarquée
- **Pydantic** - Validation des données
- **Uvicorn** - Serveur ASGI

## 📝 Notes

- L'API est configurée pour fonctionner avec la base de données SQLite existante
- Aucune configuration supplémentaire n'est nécessaire pour une utilisation locale
- Pour le développement, le mode `--reload` permet un rechargement automatique lors des modifications
