# API de Gestion de Bibliothèque avec FastAPI

## 📋 Prérequis

- Python 3.8+
- pip (gestionnaire de paquets Python)
- Un terminal ou invite de commande

## 🚀 Installation

1. **Cloner le dépôt**
   ```bash
   git clone [URL_DU_REPO]
   cd Scrapy_Books
   ```

2. **Créer et activer un environnement virtuel**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   # python3 -m venv venv
   # source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

## 🏃‍♂️ Démarrer l'API

```bash
# Depuis la racine du projet
uvicorn books_api.presentation.main:app --reload
```

## 🔍 Accès à l'API

- **Documentation interactive (Swagger UI)**: http://127.0.0.1:8000/docs
- **Documentation alternative (ReDoc)**: http://127.0.0.1:8000/redoc
- **Vérification de l'état**: http://127.0.0.1:8000/health

## 🔐 Authentification

L'API utilise l'authentification HTTP Basic. Utilisez ces identifiants par défaut :
- **Utilisateur** : `admin`
- **Mot de passe** : `admin123`

## 📚 Endpoints de l'API

### 📖 Gestion des Livres
- `GET /api/v1/books` - Liste paginée des livres
- `GET /api/v1/books/{book_id}` - Détails d'un livre spécifique
- `GET /api/v1/books/search/?q=terme` - Recherche de livres par titre ou catégorie

### 📊 Statistiques
- `GET /api/v1/stats` - Statistiques sur la collection de livres

### 🩺 Santé de l'API
- `GET /health` - Vérifie que l'API est opérationnelle

## 🏗️ Structure du Projet

```
Scrapy_Books/
│
├── books_api/                  # API FastAPI
│   ├── data/                   # Couche d'accès aux données
│   │   ├── book_repository.py  # Opérations CRUD sur les livres
│   │   ├── sqlite.py           # Configuration SQLite
│   │   └── config.py           # Configuration de l'application
│   │
│   ├── domain/                 # Logique métier
│   │   ├── book.py            # Modèle de domaine Livre
│   │   ├── user.py            # Modèle de domaine Utilisateur
│   │   └── book_usecases.py   # Cas d'utilisation métier
│   │
│   └── presentation/          # Couche présentation (API)
│       ├── main.py            # Point d'entrée FastAPI
│       ├── routes.py          # Définition des routes API
│       └── auth.py            # Gestion de l'authentification
│
├── .env.example              # Exemple de fichier de configuration
├── requirements.txt          # Dépendances du projet
└── README.md                # Ce fichier
```

## ⚙️ Configuration

Créez un fichier `.env` à la racine du projet en vous basant sur `.env.example` :

```env
# Configuration de la base de données
DATABASE_URL=sqlite:///./data/books.db
DB_TIMEOUT=30
DB_ISOLATION_LEVEL=None

# Configuration du serveur
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Authentification
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

## 🧪 Exécution des tests

```bash
# Exécuter tous les tests
pytest
```

## 🛠️ Développement

### Formattage du code
```bash
# Formater avec Black
black .

# Trier les imports avec isort
isort .
```

### Vérifications de qualité
```bash
# Vérifier les erreurs de style
flake8

# Vérifier la couverture des tests
pytest --cov=books_api tests/
```

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

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