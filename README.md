#  Scraper de Livres avec API

##  Installation

1. **Prérequis**
   - Python 3.7+
   - pip

2. **Configuration**
   ```bash
   # Cloner le projet
   git clone [URL_DU_REPO]
   cd Scrapy_Books

   # Créer et activer l'environnement
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux

   # Installer les dépendances
   pip install -r requirements.txt
   ```

##  Utilisation

1. **Lancer le scraper**
   ```bash
   cd monprojet
   scrapy crawl books
   ```
   
   Les données seront enregistrées dans : `monprojet/books.db`

2. **Démarrer l'API**
   ```bash
   cd books_api
   uvicorn presentation.main:app --reload --port 8000
   ```

3. **Accéder à l'API**
   - Documentation interactive : http://localhost:8000/docs
   - Documentation alternative : http://localhost:8000/redoc
   - Données brutes : http://localhost:8000/books/

##  Structure du Projet

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
│   ├── data/                   # Accès aux données
│   │   ├── book_repository.py  # Opérations CRUD
│   │   └── sqlite.py           # Configuration SQLite
│   ├── domain/                 # Logique métier
   │   ├── book.py             # Modèle de données
   │   └── book_usecases.py    # Cas d'utilisation
   └── presentation/           # Couche API
       ├── main.py             # Configuration FastAPI
       └── routes.py           # Définition des routes
│
├── requirements.txt           # Dépendances du projet
└── README.md                 # Ce fichier
```

##  Configuration

Créez un fichier `.env` à la racine :

```env
# Base de données
DB_TYPE=sqlite
SQLITE_PATH=./monprojet/books.db

# Serveur API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

##  Endpoints API

### Livres
- `GET /api/v1/books` - Liste paginée des livres
- `GET /api/v1/books/{book_id}` - Détails d'un livre
- `GET /api/v1/books/search/?q=terme` - Recherche de livres

### Statistiques
- `GET /api/v1/stats` - Statistiques sur la collection
- `GET /health` - Vérification de l'état de l'API

##  Exemples de Requêtes

### Liste des livres
```http
GET /api/v1/books?skip=0&limit=10
```

### Rechercher un livre
```http
GET /api/v1/books/search/?q=python
```

##  Notes
- Les données sont stockées dans une base SQLite locale
- Le scraper peut être relancé pour mettre à jour les données
- L'API se recharge automatiquement pendant le développement