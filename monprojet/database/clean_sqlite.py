"""
Script de nettoyage de la base de données SQLite des livres.

Ce script effectue des opérations de maintenance sur la base de données,
y compris la suppression des doublons basée sur l'URL des livres.
"""

import sqlite3

# Configuration du chemin vers la base de données SQLite
# Remarque : À adapter selon l'emplacement de votre base de données
db_path = r"C:\Users\Utilisateur\Desktop\simplon_dev_ia\scr\Scrapy_Books\monprojet\books.db"

# Connexion à la base de données SQLite
try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    print(f"Connexion établie à la base de données : {db_path}")
except sqlite3.Error as e:
    print(f"Erreur lors de la connexion à la base de données : {e}")
    raise

def remove_duplicates(cursor, connection):
    """
    Supprime les doublons de la table des livres en conservant la première occurrence.
    
    Args:
        cursor: Curseur de base de données
        connection: Connexion à la base de données
    """
    print("Suppression des doublons...")
    cursor.execute("""
    DELETE FROM books
    WHERE id NOT IN (
        SELECT MIN(id)
        FROM books
        GROUP BY url
    )
    """)
    deleted_rows = cursor.rowcount
    connection.commit()
    print(f"{deleted_rows} doublons supprimés.")
    return deleted_rows

if __name__ == "__main__":
    try:
        # Suppression des doublons
        removed = remove_duplicates(cur, conn)
        
        # Vérification du nombre de livres uniques
cur.execute("SELECT COUNT(*) FROM books")
print("Nombre de livres uniques après nettoyage:", cur.fetchone()[0])

conn.close()
