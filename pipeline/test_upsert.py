"""Quick diagnostic — run from the pipeline/ folder to test DB writes."""
from config import DB_CONFIG
import mysql.connector

print("Connecting with:", {k: v for k, v in DB_CONFIG.items() if k != "password"})

conn = mysql.connector.connect(**DB_CONFIG)
print("Connected. autocommit =", conn.autocommit)

cur = conn.cursor(dictionary=True)

# 1. Check existing stores
cur.execute("SELECT * FROM stores")
print("Stores before:", cur.fetchall())

# 2. Try inserting a test store
conn.autocommit = False
try:
    cur.execute("INSERT IGNORE INTO stores (name) VALUES ('TEST_STORE')")
    cur.execute("SELECT * FROM stores WHERE name = 'TEST_STORE'")
    row = cur.fetchone()
    print("Inserted row visible in transaction:", row)
    conn.commit()
    print("Committed OK")
except Exception as e:
    conn.rollback()
    print("ERROR:", e)
finally:
    conn.autocommit = True

# 3. Verify it's actually in the DB
cur.execute("SELECT * FROM stores WHERE name = 'TEST_STORE'")
print("After commit, store in DB:", cur.fetchone())

# 4. Clean up
conn.autocommit = False
cur.execute("DELETE FROM stores WHERE name = 'TEST_STORE'")
conn.commit()
conn.autocommit = True

cur.close()
conn.close()
print("Done.")
