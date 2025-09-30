import sqlite3

# Connexion à SQLite
conn = sqlite3.connect('books.db')
cur = conn.cursor()

print("📊 Statistiques sur les livres dans SQLite\n")

# 1. Prix moyen
cur.execute("SELECT AVG(price) FROM books;")
print("Prix moyen :", cur.fetchone()[0])

# 2. Top 10 catégories par nombre de livres
cur.execute("""
SELECT category, COUNT(*) AS cnt
FROM books
GROUP BY category
ORDER BY cnt DESC
LIMIT 10;
""")
print("\nTop 10 catégories par nombre de livres :")
for row in cur.fetchall():
    print(row)

# 3. Prix moyen par catégorie
cur.execute("""
SELECT category, AVG(price) AS avg_price
FROM books
GROUP BY category
ORDER BY avg_price DESC
LIMIT 10;
""")
print("\nPrix moyen par catégorie :")
for row in cur.fetchall():
    print(row)

# 4. Livres les mieux notés (rating) et leur prix
cur.execute("""
SELECT title, rating, price
FROM books
ORDER BY rating DESC, price DESC
LIMIT 20;
""")
print("\nTop 20 livres par rating et prix :")
for row in cur.fetchall():
    print(row)

conn.close()
