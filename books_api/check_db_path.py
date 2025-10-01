import os
from app.data.config.config import SQLITE_PATH

print(f"Chemin de la base de données : {SQLITE_PATH}")
print(f"Le fichier existe : {os.path.exists(SQLITE_PATH)}")
print(f"Permissions de lecture : {os.access(SQLITE_PATH, os.R_OK) if os.path.exists(SQLITE_PATH) else 'N/A'}")
print(f"Permissions d'écriture : {os.access(SQLITE_PATH, os.W_OK) if os.path.exists(SQLITE_PATH) else 'N/A'}")
