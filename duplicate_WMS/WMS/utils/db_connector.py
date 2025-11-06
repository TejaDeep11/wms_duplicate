import mysql.connector.pooling
import mysql.connector.errors
import os
from dotenv import load_dotenv

load_dotenv()

try:
    db_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="wms_pool",
        pool_size=5,
        host='localhost',
        user='root',
        password='Root1234!',
        database='wms_db'
    )
    print("Database connection pool created successfully.")
except mysql.connector.Error as err:
    print(f"Error creating connection pool: {err}")
    exit()

def fetch_one(query, params=None):
    """
    Fetches a single record from the database.
    """
    conn = None
    cursor = None
    try:
        conn = db_pool.get_connection()
        conn.ping(reconnect=True) 
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(query, params or ())
        return cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Database Fetch Error (fetch_one): {err}")
        return None
    finally:
        if cursor: 
            cursor.close()
        if conn:
            try:
                conn.close()
            except mysql.connector.Error as e:
                print(f"Error closing connection (fetch_one): {e}")

def fetch_all(query, params=None):
    """
    Fetches all records from the database.
    """
    conn = None
    cursor = None
    try:
        conn = db_pool.get_connection()
        conn.ping(reconnect=True) 
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(query, params or ())
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Database Fetch Error (fetch_all): {err}")
        return None
    finally:
        if cursor: 
            cursor.close()
        if conn:
            try:
                conn.close()
            except mysql.connector.Error as e:
                print(f"Error closing connection (fetch_all): {e}")

def execute_query(query, params=None):
    """
    Executes an INSERT, UPDATE, or DELETE query.
    """
    conn = None
    cursor = None
    try:
        conn = db_pool.get_connection()
        conn.ping(reconnect=True) 
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        
        if cursor.lastrowid:
            return cursor.lastrowid
        return cursor.rowcount
    except mysql.connector.Error as err:
        print(f"Database Execute Error (execute_query): {err}")
        return None
    finally:
        if cursor: 
            cursor.close()
        if conn:
            try:
                conn.close()
            except mysql.connector.Error as e:
                print(f"Error closing connection (execute_query): {e}")