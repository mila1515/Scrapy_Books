import sqlite3

# Ouvrir la base SQLite
conn = sqlite3.connect('books.db')
cur = conn.cursor()

# Afficher le nombre total de livres
cur.execute("SELECT COUNT(*) FROM books;")
print("Nombre de livres :", cur.fetchone()[0])

# Afficher les 5 premiers livres
cur.execute("SELECT * FROM books LIMIT 5;")
for row in cur.fetchall():
    print(row)

conn.close()
