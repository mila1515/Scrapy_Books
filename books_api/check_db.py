import sqlite3
import os

# Chemin vers la base de données
db_path = r"c:\Users\Utilisateur\Desktop\simplon_dev_ia\scr\Scrapy_Books\monprojet\books.db"

# Vérifier si le fichier existe
if not os.path.exists(db_path):
    print(f"Erreur: Le fichier de base de données n'existe pas à l'emplacement: {db_path}")
    exit(1)

try:
    # Se connecter à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Récupérer la structure de la table books
    cursor.execute("PRAGMA table_info(books)")
    columns = cursor.fetchall()
    
    print("Structure de la table 'books':")
    for col in columns:
        print(f"- {col[1]}: {col[2]}")
    
    # Compter le nombre d'entrées
    cursor.execute("SELECT COUNT(*) FROM books")
    count = cursor.fetchone()[0]
    print(f"\nNombre total de livres dans la base de données: {count}")
    
    # Afficher un exemple de données
    if count > 0:
        cursor.execute("SELECT * FROM books LIMIT 1")
        example = cursor.fetchone()
        print("\nExemple de données:")
        for i, col in enumerate(columns):
            print(f"- {col[1]}: {example[i]}")
    
    conn.close()
    
except sqlite3.Error as e:
    print(f"Erreur lors de l'accès à la base de données: {e}")
    exit(1)
