# Projet Scrapy Books avec API

Ce projet combine un scraper Scrapy pour [books.toscrape.com](http://books.toscrape.com/) et une API RESTful FastAPI pour accéder aux données collectées.

## 📋 Fonctionnalités

- **Scraping** : Extraction des données de livres depuis books.toscrape.com
- **Stockage** : Sauvegarde dans une base de données SQLite
- **API REST** : Interface pour accéder aux données via des endpoints HTTP
- **Recherche** : Recherche de livres par titre, catégorie, prix, etc.
- **Statistiques** : Métriques sur la collection de livres

## 🚀 Installation

1. **Cloner le dépôt**
   ```bash
   git clone [URL_DU_REPO]
   cd Scrapy_Books
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv env
   env\Scripts\activate  # Sur Windows
   source env/bin/activate  # Sur macOS/Linux
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

## 🕷️ Utilisation du Scraper

1. **Lancer le scraper**
   ```bash
   cd monprojet
   scrapy crawl books
   ```
   
   Les données seront sauvegardées dans `monprojet/books.db`

## 🌐 Utilisation de l'API

1. **Démarrer le serveur API**
   ```bash
   cd books_api
   uvicorn app.main:app --reload --port 8000
   ```

2. **Accéder à la documentation**
   - Documentation interactive: http://localhost:8000/docs
   - Documentation alternative: http://localhost:8000/redoc

## 📂 Structure du projet

```
Scrapy_Books/
│
├── monprojet/                  # Projet Scrapy
│   ├── spiders/
│   │   └── scrapybooks.py      # Spider principal
│   ├── items.py                # Définition des items
│   ├── itemloaders.py          # Loaders et nettoyages
│   ├── pipelines.py            # Pipelines de traitement
│   ├── settings.py             # Configuration Scrapy
│   └── books.db                # Base de données SQLite (générée)
│
├── books_api/                  # API FastAPI
│   ├── app/
│   │   ├── core/              # Configuration
│   │   ├── data/              # Accès aux données
│   │   ├── domain/            # Logique métier
│   │   └── presentation/      # Routes et schémas
│   └── requirements.txt        # Dépendances de l'API
│
├── requirements-unified.txt    # Toutes les dépendances
└── README.md                  # Ce fichier
```

## 📚 Endpoints de l'API

- `GET /books/` - Liste tous les livres
- `GET /books/{book_id}` - Détails d'un livre spécifique
- `GET /books/search/title/{title}` - Recherche de livres par titre
- `GET /books/search/category/{category}` - Recherche par catégorie
- `GET /books/stats/summary` - Statistiques sur la collection

## Configuration

Créez un fichier `.env` à la racine du projet avec les variables nécessaires :

```env
# Configuration de la base de données
DB_TYPE=sqlite
SQLITE_PATH=./monprojet/books.db

# Pour PostgreSQL (optionnel)
# PG_DB=books_db
# PG_USER=postgres
# PG_PASSWORD=votre_mot_de_passe
# PG_HOST=localhost
# PG_PORT=5432
```

## Exécution

1. **Lancer le scraper**
   ```bash
   cd monprojet
   scrapy crawl books
   ```

2. **Démarrer l'API**
   ```bash
   cd books_api
   uvicorn app.main:app --reload --port 8000
   ```

## Vérification des données

### SQLite
```bash
sqlite3 monprojet/books.db
sqlite> SELECT COUNT(*) FROM books;
sqlite> SELECT * FROM books LIMIT 5;
```

### Via l'API
- Accédez à la documentation interactive : http://localhost:8000/docs
- Ou consultez directement : http://localhost:8000/books/

## Notes techniques

- Les doublons sont automatiquement ignorés (basé sur l'URL)
- Le middleware gère automatiquement les User-Agents
- La pagination est gérée automatiquement par le spider