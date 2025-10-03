# Scrapy Books - Outil de Scraping et API REST

Un projet complet pour extraire des données de livres depuis le web et les exposer via une API RESTful sécurisée.

## 📋 Fonctionnalités

### 🕷️ Module de Scraping
- Extraction de données de livres depuis des sites web
- Gestion des requêtes asynchrones
- Nettoyage et traitement des données
- Stockage dans une base de données SQLite

### 🌐 API REST
- Documentation interactive (Swagger/ReDoc)
- Authentification sécurisée
- Gestion complète des livres (CRUD)
- Recherche avancée par catégories, titres, etc.
- Statistiques sur la collection de livres

## 🚀 Prérequis

- Python 3.8+
- pip (gestionnaire de paquets Python)
- Git (optionnel)

## 🛠 Installation

1. **Cloner le dépôt**
   ```bash
   git clone [URL_DU_REPO]
   cd Scrapy_Books
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   ```

3. **Activer l'environnement virtuel**
   - Windows : `.\venv\Scripts\activate`
   - macOS/Linux : `source venv/bin/activate`

4. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙ Configuration

1. **Configurer l'environnement**
   Créez un fichier `.env` dans le dossier `monprojet/` :
   ```env
   # Authentification API
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=votre_mot_de_passe_secure
   
   # Base de données
   DATABASE_URL=sqlite:///monprojet/books.db
   
   # Configuration Scrapy (si nécessaire)
   USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."
   ```

## 🕷️ Utilisation du Scraper

1. **Lancer le spider**
   ```bash
   cd monprojet
   scrapy crawl nom_du_spider -o livres.json
   ```

   Options disponibles :
   - `-o output.json` : Exporter les résultats
   - `-s LOG_LEVEL=INFO` : Niveau de logs
   - `-a param=valeur` : Passer des paramètres au spider

2. **Exécuter les tests du scraper**
   ```bash
   cd monprojet
   scrapy check
   ```

## 🌐 Utilisation de l'API

1. **Démarrer le serveur**
   ```bash
   python run.py
   ```

2. **Accès à la documentation**
   - Swagger UI : http://127.0.0.1:8000/docs
   - ReDoc : http://127.0.0.1:8000/redoc

3. **Authentification**
   ```
   Utilisateur: admin
   Mot de passe: [votre_mot_de_passe]
   ```

## 🧪 Tests

Le projet inclut une suite complète de tests pour assurer la qualité et la fiabilité du code. Voici comment exécuter et gérer les tests :

### Exécuter tous les tests

```bash
# Depuis la racine du projet
python -m pytest books_api/tests/ -v
```



## 📚 Structure du Projet

```
Scrapy_Books/
├── books_api/                  # Code source de l'API
│   ├── data/                   # Accès aux données
│   │   ├── book_repository.py  # Gestion des opérations CRUD
│   │   ├── config.py           # Configuration de l'application
│   │   └── sqlite.py           # Gestion de la base de données
│   │
│   ├── domain/                 # Logique métier
│   │   ├── book.py            # Modèle de données Livre
│   │   ├── book_usecases.py   # Cas d'utilisation métier
│   │   └── user.py            # Gestion des utilisateurs
│   │
│   └── presentation/          # Gestion des requêtes
│       ├── auth.py            # Authentification
│       ├── main.py            # Application FastAPI
│       └── routes.py          # Définition des routes API
│
├── monprojet/                 # Projet Scrapy
│   └── monprojet/
│       ├── spiders/           # Spiders de scraping
│       │   ├── __init__.py   # Fichier d'initialisation
│       │   └── scrapybooks.py  # Spider principal pour le scraping de livres
│       │
│       ├── __init__.py
│       ├── items.py          # Modèles de données Scrapy
│       ├── middlewares.py    # Middlewares personnalisés
│       ├── pipelines.py      # Traitement des données
│       ├── settings.py       # Configuration Scrapy
│       └── .env             # Configuration d'environnement
│
├── .gitignore
├── requirements.txt         # Dépendances du projet
└── run.py                   # Point d'entrée de l'application
```

## 🧪 Tests

### Tester l'API
```bash
pytest books_api/tests/
```

### Tester les spiders
```bash
cd monprojet
scrapy check
```
