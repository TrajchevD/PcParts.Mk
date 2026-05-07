from contextlib import contextmanager
from mysql.connector import pooling
from app.core.config import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME
from app.core.constants import DB_POOL_SIZE

_pool = pooling.MySQLConnectionPool(
    pool_name="main_pool",
    pool_size=DB_POOL_SIZE,
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME,
    autocommit=True,
)


@contextmanager
def get_db():
    conn = _pool.get_connection()
    try:
        yield conn
    finally:
        conn.close()


def fetchall(sql: str, params: tuple = ()) -> list[dict]:
    with get_db() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(sql, params)
            return cur.fetchall()
        finally:
            cur.close()


def fetchone(sql: str, params: tuple = ()) -> dict | None:
    with get_db() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(sql, params)
            return cur.fetchone()
        finally:
            cur.close()


def execute(sql: str, params: tuple = ()) -> int:
    """Executes a single statement and returns lastrowid."""
    with get_db() as conn:
        cur = conn.cursor()
        try:
            cur.execute(sql, params)
            return cur.lastrowid
        finally:
            cur.close()


