import os
from dotenv import load_dotenv

# Chemin vers la base de données SQLite existante
# Remonter d'un niveau supplémentaire pour atteindre le dossier monprojet
SQLITE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "monprojet", "books.db"))

# Vérifier que le fichier existe
if not os.path.exists(SQLITE_PATH):
    raise FileNotFoundError(f"Le fichier de base de données n'existe pas à l'emplacement : {SQLITE_PATH}")

# Vérifier les permissions
if not os.access(SQLITE_PATH, os.R_OK | os.W_OK):
    raise PermissionError(f"Permissions insuffisantes pour accéder au fichier : {SQLITE_PATH}")
