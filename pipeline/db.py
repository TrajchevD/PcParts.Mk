import mysql.connector
from mysql.connector import pooling
from config import DB_CONFIG

_pool = pooling.MySQLConnectionPool(
    pool_name="pipeline",
    pool_size=10,
    autocommit=True,
    **DB_CONFIG,
)


def get_conn():
    return _pool.get_connection()


def fetchall(sql, params=()):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        conn.close()


def execute(sql, params=()):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
    finally:
        conn.close()
