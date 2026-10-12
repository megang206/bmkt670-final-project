import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

db_password = os.getenv("DB_PASSWORD", "your_password_here")
db_name = os.getenv("DB_NAME", "postgres")
db_user = os.getenv("DB_USER", "postgres")
db_host = os.getenv("DB_HOST", "localhost")

try:
    connection = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port="5432"
    )
    cursor = connection.cursor()
    
    # Query to check existing tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public';
    """)
    
    tables = cursor.fetchall()
    print("Successfully connected to PostgreSQL!")
    print("Tables found in database:")
    for table in tables:
        print(f" - {table[0]}")
        
    cursor.close()
    connection.close()
except Exception as e:
    print("Database connection failed. Make sure your .env password is correct and Postgres is running.")
    print("Error details:", e)