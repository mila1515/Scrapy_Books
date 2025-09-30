import sqlite3

# Connexion à la base SQLite
conn = sqlite3.connect('books.db')
cur = conn.cursor()

print("📊 Statistiques sur les livres\n")
print("="*50)

# 1️⃣ Prix moyen de tous les livres
cur.execute("SELECT AVG(price) FROM books;")
prix_moyen = cur.fetchone()[0]
print(f"\n1️⃣ Prix moyen de tous les livres : {prix_moyen:.2f} €")

# 2️⃣ Top 10 catégories par nombre de livres
cur.execute("""
SELECT category, COUNT(*) AS nb_livres
FROM books
GROUP BY category
ORDER BY nb_livres DESC
LIMIT 10;
""")
top_categories = cur.fetchall()
print("\n2️⃣ Top 10 catégories par nombre de livres :")
for i, (category, nb) in enumerate(top_categories, start=1):
    print(f"{i}. {category} → {nb} livres")

# 3️⃣ Prix moyen par catégorie
cur.execute("""
SELECT category, AVG(price) AS prix_moyen
FROM books
GROUP BY category
ORDER BY prix_moyen DESC
LIMIT 10;
""")
prix_par_categorie = cur.fetchall()
print("\n3️⃣ Prix moyen par catégorie (Top 10) :")
for i, (category, avg_price) in enumerate(prix_par_categorie, start=1):
    print(f"{i}. {category} → {avg_price:.2f} €")

# 4️⃣ Top 20 livres par note et prix
cur.execute("""
SELECT title, rating, price
FROM books
ORDER BY rating DESC, price DESC
LIMIT 20;
""")
top_livres = cur.fetchall()
print("\n4️⃣ Top 20 livres par note et prix :")
for i, (title, rating, price) in enumerate(top_livres, start=1):
    print(f"{i}. '{title}' → Note: {rating}, Prix: {price:.2f} €")

# Fermeture de la connexion
conn.close()
print("\n✅ Analyse terminée.")
