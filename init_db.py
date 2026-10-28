"""Database initialization script.

Executes all database scripts in order:
1. schema.sql
2. views.sql
3. procedures.sql
4. triggers.sql
5. seed.sql
"""
import os
import sys
import pymysql
from config import Config
from werkzeug.security import generate_password_hash


def run_sql_file(cursor, file_path):
    """Read and execute a SQL file containing multiple statements, handling DELIMITER blocks."""
    print(f"Executing: {os.path.basename(file_path)}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by DELIMITER or execute statement by statement
    delimiter = ';'
    current_statement = []
    
    lines = content.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped.upper().startswith('DELIMITER'):
            # Change delimiter
            parts = stripped.split()
            if len(parts) > 1:
                delimiter = parts[1]
            continue

        if not stripped or stripped.startswith('--') or stripped.startswith('/*'):
            continue

        current_statement.append(line)

        # Check if statement ends with the active delimiter
        if stripped.endswith(delimiter):
            stmt = '\n'.join(current_statement)
            # Remove trailing delimiter
            if delimiter != ';':
                stmt = stmt.rstrip()
                if stmt.endswith(delimiter):
                    stmt = stmt[:-len(delimiter)].strip()
            else:
                stmt = stmt.rstrip(';').strip()

            if stmt:
                try:
                    cursor.execute(stmt)
                except Exception as e:
                    print(f"  Warning executing statement:\n  {stmt[:80]}...\n  Error: {e}\n")
            current_statement = []

    print(f"  Completed: {os.path.basename(file_path)}")


def init_database():
    """Connect to MySQL, run all SQL scripts, and seed default administrator."""
    print("=" * 60)
    print("Campus Placement & Eligibility Management System - DB Setup")
    print("=" * 60)
    print(f"Connecting to MySQL at {Config.MYSQL_HOST}:{Config.MYSQL_PORT} as {Config.MYSQL_USER}...")

    try:
        # First connect without specifying database to create database if not exists
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            charset='utf8mb4',
            autocommit=True
        )
    except Exception as e:
        print(f"\n[ERROR] Could not connect to MySQL server: {e}")
        print("\nPlease ensure MySQL 8 is running and credentials in .env or environment variables are correct.")
        sys.exit(1)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(base_dir, 'database')

    sql_files = [
        os.path.join(db_dir, 'schema.sql'),
        os.path.join(db_dir, 'views.sql'),
        os.path.join(db_dir, 'procedures.sql'),
        os.path.join(db_dir, 'triggers.sql'),
        os.path.join(db_dir, 'seed.sql'),
    ]

    try:
        with conn.cursor() as cursor:
            for sql_file in sql_files:
                if os.path.exists(sql_file):
                    run_sql_file(cursor, sql_file)
                else:
                    print(f"File not found: {sql_file}")

            # Update admin password hash to valid Werkzeug hash for 'admin123'
            print("Configuring demo administrator account (admin / admin123)...")
            cursor.execute("USE campus_placement")
            hashed = generate_password_hash('admin123')
            cursor.execute(
                "UPDATE admin_users SET password_hash = %s WHERE username = 'admin'",
                (hashed,)
            )

        print("\nDatabase initialization and seeding completed successfully!")
        print("Ready to run the application: python app.py")
        print("=" * 60)

    finally:
        conn.close()


if __name__ == '__main__':
    init_database()
