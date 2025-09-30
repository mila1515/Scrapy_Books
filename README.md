# Scrapy Books - Scraper avec SQLite et PostgreSQL

Ce projet Scrapy scrape le site [books.toscrape.com](http://books.toscrape.com/) et stocke les données des livres dans **SQLite** et **PostgreSQL** en parallèle.

---

## 📂 Structure du projet

monprojet/
│
├── spiders/
│ └── scrapybooks.py # Spider principal
│
├── items.py # Définition des items
├── itemloaders.py # Loaders et nettoyages
├── pipelines.py # Pipelines SQLite et PostgreSQL
├── middlewares.py # Middleware avec User-Agent
├── settings.py # Paramètres Scrapy
├── books.db # Base SQLite (après le premier run)
├── .env # Variables d'environnement
└── scrapy.cfg


## ⚙️ Installation

1. Clone le projet :

```bash
git clone <repo_url>
cd monprojet


2. Crée et active un environnement virtuel (optionnel mais recommandé) :
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows


3. Installe les dépendances :

pip install -r requirements.txt


4.  ⚙️ Configuration du fichier `.env`

Crée un fichier `.env` à la racine du projet et ajoute tes informations de base de données comme suit :

```env
# Chemin vers la base SQLite
SQLITE_PATH=  chemin complet vers ta base SQLite.
# Informations PostgreSQL
PG_DB= nom de la base PostgreSQL.
PG_USER= utilisateur PostgreSQL.
PG_PASSWORD= mot de passe PostgreSQL.
PG_HOST= hôte PostgreSQL (souvent localhost).
PG_PORT= port PostgreSQL (par défaut 5432).




## 🏃 Lancer le spider
scrapy crawl scrapybooks

Les données seront ajoutées dans SQLite (books.db) et dans PostgreSQL (books_db).
Les doublons sur l’URL sont ignorés.
Si le stock est introuvable, la valeur est -1 et un warning est affiché dans les logs.


## 🔧 Vérification des bases

SQLite:

sqlite3 books.db
sqlite> SELECT COUNT(*) FROM books;
sqlite> SELECT * FROM books LIMIT 5;


PostgreSQL:

-- Connecte-toi à la base
\c books_db
SELECT COUNT(*) FROM books;
SELECT * FROM books LIMIT 5;


⚡ Notes

User-Agent géré via middleware pour rotation ou randomisation.
Stock : si absent, devient -1 dans les bases.
Pagination automatique.
Pipelines SQLite et PostgreSQL en parallèle.