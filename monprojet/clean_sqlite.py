import sqlite3

conn = sqlite3.connect("books.db")
cur = conn.cursor()

# Supprimer les doublons sur title + url en gardant la première occurrence
cur.execute("""
DELETE FROM books
WHERE id NOT IN (
    SELECT MIN(id)
    FROM books
    GROUP BY title, url
)
""")
conn.commit()

# Vérifier le nombre de livres uniques
cur.execute("SELECT COUNT(*) FROM books")
print("Nombre de livres uniques :", cur.fetchone()[0])

conn.close()
