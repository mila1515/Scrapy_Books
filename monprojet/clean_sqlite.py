import sqlite3

# Chemin vers ta base
db_path = r"C:\Users\Utilisateur\Desktop\simplon_dev_ia\scr\Scrapy_Books\monprojet\books.db"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Supprimer les doublons en gardant la première occurrence
cur.execute("""
DELETE FROM books
WHERE id NOT IN (
    SELECT MIN(id)
    FROM books
    GROUP BY url
)
""")
conn.commit()

# Vérifier combien de livres uniques restent
cur.execute("SELECT COUNT(*) FROM books")
print("Nombre de livres uniques après nettoyage:", cur.fetchone()[0])

conn.close()
