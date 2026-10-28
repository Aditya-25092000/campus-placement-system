"""Database connection manager for MySQL using PyMySQL."""
import pymysql
from config import Config


def get_db_connection():
    """Get a new database connection with DictCursor."""
    connection = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )
    return connection


def execute_query(query, params=None, fetchone=False, fetchall=True):
    """Execute a SELECT query and return results."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if fetchone:
                return cursor.fetchone()
            if fetchall:
                return cursor.fetchall()
            return None
    finally:
        conn.close()


def execute_update(query, params=None):
    """Execute an INSERT/UPDATE/DELETE query. Returns (lastrowid, rowcount)."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid, cursor.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_transaction(queries_and_params):
    """Execute multiple queries in a single transaction.

    Args:
        queries_and_params: list of (query, params) tuples
    Returns:
        List of (lastrowid, rowcount) for each query
    """
    conn = get_db_connection()
    conn.autocommit(False)
    results = []
    try:
        with conn.cursor() as cursor:
            for query, params in queries_and_params:
                cursor.execute(query, params)
                results.append((cursor.lastrowid, cursor.rowcount))
            conn.commit()
        return results
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.autocommit(True)
        conn.close()


def call_procedure(proc_name, args=None):
    """Call a stored procedure and return results."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc(proc_name, args or [])
            return cursor.fetchall()
    finally:
        conn.close()
