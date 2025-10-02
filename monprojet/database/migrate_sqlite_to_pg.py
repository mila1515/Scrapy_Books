"""
Script de migration de données de SQLite vers PostgreSQL.

Ce script permet de transférer les données d'une base SQLite vers une base PostgreSQL.
Il est conçu pour être utilisé avec le projet de scraping de livres.

Prérequis :
- Un fichier .env contenant les informations de connexion PostgreSQL
- Les bibliothèques : psycopg2, python-dotenv
"""

import sqlite3
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values
import os

def load_environment():
    """
    Charge les variables d'environnement depuis le fichier .env
    
    Returns:
        bool: True si le chargement a réussi, False sinon
    """
    try:
        load_dotenv()
        return True
    except Exception as e:
        print(f"Erreur lors du chargement des variables d'environnement : {e}")
        return False

def connect_sqlite(db_path):
    """
    Établit une connexion à la base de données SQLite.
    
    Args:
        db_path (str): Chemin vers le fichier de base de données SQLite
        
    Returns:
        tuple: (connexion, curseur) ou (None, None) en cas d'erreur
    """
    try:
        conn = sqlite3.connect(db_path)
        return conn, conn.cursor()
    except sqlite3.Error as e:
        print(f"Erreur de connexion à SQLite : {e}")
        return None, None

def connect_postgres():
    """
    Établit une connexion à la base de données PostgreSQL.
    
    Returns:
        tuple: (connexion, curseur) ou (None, None) en cas d'erreur
    """
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("PG_DB"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT")
        )
        return conn, conn.cursor()
    except psycopg2.Error as e:
        print(f"Erreur de connexion à PostgreSQL : {e}")
        return None, None

def create_pg_table(cursor):
    """
    Crée la table dans PostgreSQL si elle n'existe pas.
    
    Args:
        cursor: Curseur de la base de données PostgreSQL
        
    Returns:
        bool: True si la création a réussi, False sinon
    """
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
            title TEXT,
            price NUMERIC,
            rating NUMERIC,
            category TEXT,
            stock INTEGER,
            created_at TIMESTAMP,
            url TEXT UNIQUE
        )
        """)
        return True
    except Exception as e:
        print(f"Erreur lors de la création de la table : {e}")
        return False

def migrate_data(sqlite_cursor, pg_cursor, pg_connection):
    """
    Migre les données de SQLite vers PostgreSQL.
    
    Args:
        sqlite_cursor: Curseur de la base SQLite
        pg_cursor: Curseur de la base PostgreSQL
        pg_connection: Connexion à la base PostgreSQL
        
    Returns:
        int: Nombre de livres migrés
    """
    try:
        # Récupérer les données de SQLite
        sqlite_cursor.execute("SELECT * FROM books")
        books = sqlite_cursor.fetchall()
        
        if not books:
            print("Aucune donnée à migrer.")
            return 0
            
        # Préparer les données
        data = [(
            book[1],  # title
            book[2],  # price
            book[3],  # rating
            book[4],  # category
            book[5],  # stock
            book[6],  # created_at
            book[7]   # url
        ) for book in books]
        
        # Utiliser execute_values pour une insertion plus efficace
        execute_values(
            pg_cursor,
            """
            INSERT INTO books (title, price, rating, category, stock, created_at, url)
            VALUES %s
            ON CONFLICT (url) DO NOTHING
            """,
            data
        )
        
        pg_connection.commit()
        print(f"{len(books)} livres migrés avec succès vers PostgreSQL!")
        return len(books)
        
    except Exception as e:
        print(f"Erreur lors de la migration des données : {e}")
        pg_connection.rollback()
        return 0

def main():
    """Fonction principale du script de migration."""
    # Charger les variables d'environnement
    if not load_environment():
        return
    
    # Établir les connexions
    sqlite_conn, sqlite_cur = connect_sqlite(os.getenv("SQLITE_PATH"))
    pg_conn, pg_cur = connect_postgres()
    
    if not all([sqlite_conn, sqlite_cur, pg_conn, pg_cur]):
        print("Échec de la connexion à une des bases de données.")
        return
    
    try:
        # Créer la table et migrer les données
        if create_pg_table(pg_cur):
            migrate_data(sqlite_cur, pg_cur, pg_conn)
    finally:
        # Toujours fermer les connexions
        sqlite_conn.close()
        pg_cur.close()
        pg_conn.close()

if __name__ == "__main__":
    main()
