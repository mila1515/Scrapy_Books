# 📚 Projet Scrapy Books avec API REST

Ce projet combine un scraper Scrapy pour [books.toscrape.com](http://books.toscrape.com/) et une API RESTful FastAPI simplifiée pour accéder aux données collectées.

## 🚀 Fonctionnalités

### Scraping
- Extraction complète des données de livres depuis books.toscrape.com
- Gestion des catégories et des détails des livres
- Sauvegarde dans une base de données SQLite (`monprojet/books.db`)

### API REST
- Authentification HTTP Basic simple
- Endpoints RESTful pour accéder aux livres et catégories
- Documentation interactive (Swagger/ReDoc)
- Filtrage par catégorie et prix
- Configuration CORS pour le développement
- Gestion des erreurs et reprise sur erreur

## 🛠 Installation

### Prérequis
- Python 3.8+
- pip (gestionnaire de paquets Python)
- Git (optionnel)

### Configuration

1. **Cloner le dépôt**
   ```bash
   git clone [URL_DU_REPO]
   cd Scrapy_Books
   ```

2. **Créer et activer un environnement virtuel** (recommandé)
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
   # Installer les dépendances du scraping
   pip install -r requirements.txt
   
   # Installer les dépendances de l'API
   cd books_api
   pip install -r requirements.txt
   cd ..
   ```

## 🚀 Utilisation

### 1. Lancer le scraper

```bash
cd monprojet
scrapy crawl books -o books.json
```

### 2. Démarrer l'API

```bash
cd books_api
uvicorn app.main:app --reload
```

L'API sera disponible à l'adresse : http://127.0.0.1:8000

## 📚 Documentation de l'API

### Authentification
L'API utilise l'authentification HTTP Basic :
- **Utilisateur** : `admin`
- **Mot de passe** : `admin123`

### Endpoints disponibles

#### Livres
- `GET /api/books/` - Liste tous les livres
  - Paramètres optionnels :
    - `category` : Filtrer par catégorie
    - `min_price` : Prix minimum
    - `max_price` : Prix maximum

- `GET /api/books/{book_id}` - Récupère un livre par son ID

- `GET /api/books/categories/` - Liste toutes les catégories disponibles

### Documentation interactive
- **Swagger UI** : http://127.0.0.1:8000/docs
- **ReDoc** : http://127.0.0.1:8000/redoc

## 🔧 Configuration avancée

### Changer les identifiants d'accès
Pour modifier les identifiants d'accès, éditez le fichier :
`books_api/app/presentation/auth_routes.py`

### Configuration CORS
Pour modifier les paramètres CORS, éditez le fichier :
`books_api/app/main.py`

## 📝 Exemples de requêtes

### Avec cURL
```bash
# Récupérer tous les livres
curl -u admin:admin123 http://localhost:8000/api/books/

# Filtrer par catégorie
curl -u admin:admin123 "http://localhost:8000/api/books/?category=Fiction"

# Récupérer un livre spécifique
curl -u admin:admin123 http://localhost:8000/api/books/1
```

### Avec Python (requests)
```python
import requests
from requests.auth import HTTPBasicAuth

# Configuration de base
BASE_URL = "http://localhost:8000/api"
auth = HTTPBasicAuth("admin", "admin123")

# Récupérer tous les livres
response = requests.get(f"{BASE_URL}/books/", auth=auth)
print(response.json())

# Filtrer par catégorie
response = requests.get(
    f"{BASE_URL}/books/",
    params={"category": "Fiction"},
    auth=auth
)
print(response.json())
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/ma-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajouter ma fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/ma-fonctionnalite`)
5. Créez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Contact

Pour toute question ou suggestion, veuillez ouvrir une issue sur le dépôt.

## 📋 Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- SQLite (inclus avec Python)

## 🛠 Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/votre-utilisateur/Scrapy_Books.git
   cd Scrapy_Books
   ```

2. **Créer et activer un environnement virtuel**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement**
   Créez un fichier `.env` à la racine du projet :
   ```env
   # Configuration de la base de données
   DATABASE_URL=sqlite:///monprojet/books.db
   
   # Configuration JWT
   SECRET_KEY=votre_clé_secrète_très_longue_et_sécurisée
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

## 🕷 Utilisation du Scraper

1. **Lancer le scraper**
   ```bash
   cd monprojet
   scrapy crawl books
   ```
   
   Les données seront sauvegardées dans `monprojet/books.db`

2. **Options de scraping**
   ```bash
   # Limiter le nombre de pages à scraper
   scrapy crawl books -s CLOSESPIDER_PAGECOUNT=10
   
   # Changer le niveau de log
   scrapy crawl books --loglevel=INFO
   
   # Sauvegarder les résultats dans un fichier JSON
   scrapy crawl books -o livres.json
   ```

## 🌐 Utilisation de l'API

1. **Démarrer le serveur API**
   ```bash
   # Mode développement (avec rechargement automatique)
   uvicorn books_api.app.main:app --reload --port 8000
   
   # Mode production
   uvicorn books_api.app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

2. **Accéder à la documentation**
   - Swagger UI (interactive): http://localhost:8000/docs
   - ReDoc (documentation): http://localhost:8000/redoc

3. **Authentification**
   ```bash
   # Obtenir un token
   curl -X POST "http://localhost:8000/api/v1/token" \
   -H "Content-Type: application/x-www-form-urlencoded" \
   -d "username=admin&password=admin123"
   
   # Utiliser le token
   curl -X GET "http://localhost:8000/api/v1/books/" \
   -H "Authorization: Bearer VOTRE_TOKEN_JWT"
   ```

## 🏗 Structure du projet

```
Scrapy_Books/
│
├── monprojet/                  # Projet Scrapy
│   ├── spiders/
│   │   └── scrapybooks.py      # Spider principal
│   ├── items.py                # Définition des items
│   ├── itemloaders.py          # Loaders et nettoyages
│   ├── pipelines.py            # Pipelines de traitement
│   └── settings.py             # Configuration Scrapy
│
├── books_api/                  # API FastAPI
│   ├── app/
│   │   ├── data/              # Accès aux données
│   │   │   ├── config.py      # Configuration et sécurité
│   │   │   ├── models.py      # Modèles SQLAlchemy
│   │   │   └── repositories/   # Répertoires d'accès aux données
│   │   │
│   │   ├── domain/            # Logique métier
│   │   │   ├── entities/      # Entités du domaine
│   │   │   └── services/      # Services métier
│   │   │
│   │   └── presentation/      # Couche présentation
│   │       ├── api/           # Routeurs FastAPI
│   │       ├── schemas.py     # Modèles Pydantic
│   │       └── dependencies.py # Dépendances d'API
│   │
│   ├── tests/                 # Tests automatisés
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   └── test_*.py
│   │
│   └── main.py                # Point d'entrée de l'application
│
├── .env.example               # Exemple de configuration
├── requirements.txt           # Dépendances Python
└── README.md                  # Ce fichier

```

## 🔧 Exécution des tests

```bash
# Exécuter tous les tests
pytest books_api/tests/ -v

# Exécuter les tests avec couverture de code
pytest --cov=books_api books_api/tests/

# Générer un rapport de couverture HTML
pytest --cov=books_api --cov-report=html books_api/tests/
```

## 📊 Vérification des données

### SQLite
```bash
sqlite3 monprojet/books.db
sqlite> SELECT COUNT(*) FROM books;
sqlite> SELECT * FROM books LIMIT 5;
```

### Via l'API
- Documentation interactive : http://localhost:8000/docs
- Documentation alternative : http://localhost:8000/redoc
- Endpoint des livres : http://localhost:8000/api/v1/books/

## 🔒 Sécurité

- Authentification JWT requise pour les opérations sensibles
- Hachage des mots de passe avec bcrypt
- Protection contre les attaques CSRF
- Headers de sécurité HTTP
- Validation stricte des entrées

## 🚀 Déploiement

### Préparation pour la production
1. Mettre à jour les variables d'environnement dans `.env`
2. Changer la clé secrète JWT
3. Configurer une base de données de production (PostgreSQL recommandé)
4. Configurer un serveur web (Nginx/Apache) avec Gunicorn/Uvicorn

### Variables d'environnement requises
```env
# Production
SECRET_KEY=votre_clé_secrète_très_longue_et_sécurisée
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=postgresql://user:password@localhost:5432/books_db

# Développement
# DATABASE_URL=sqlite:///monprojet/books.db
```

## 🤝 Contribution

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.

## 📞 Contact

Votre Nom - [@votre_twitter](https://twitter.com/votre_twitter) - email@exemple.com

Lien du projet : [https://github.com/votre-utilisateur/Scrapy_Books](https://github.com/votre-utilisateur/Scrapy_Books)

## 🙏 Remerciements

- [FastAPI](https://fastapi.tiangolo.com/)
- [Scrapy](https://scrapy.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [Uvicorn](https://www.uvicorn.org/)

- Les doublons sont automatiquement ignorés (basé sur l'URL)
- Le middleware gère automatiquement les User-Agents
- La pagination est gérée automatiquement par le spider