import mysql.connector
from mysql.connector import pooling
from app.settings import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME

print("🔥 CONNECTING TO DB:", DB_NAME)

_pool = pooling.MySQLConnectionPool(
    pool_name="price_pool",
    pool_size=10,
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME,
    autocommit=True,
)

def get_conn():
    return _pool.get_connection()


def execute(sql: str, params: tuple = ()):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()


def fetchall(sql: str, params: tuple = ()):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

