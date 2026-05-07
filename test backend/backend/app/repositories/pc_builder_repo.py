from app.db import fetchall, execute, get_conn
from app.db import fetchall


SLOTS = ["cpu","mb","ram","gpu","storage"]

def create_build(user_id: int, name: str) -> int:
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        "INSERT INTO builds(user_id, name) VALUES (%s, %s)",
        (user_id, name),
    )
    build_id = cur.lastrowid

    slots = ["cpu", "mb", "ram", "gpu", "storage"]
    for slot in slots:
        cur.execute(
            "INSERT INTO build_parts(build_id, slot, product_id) VALUES (%s, %s, NULL)",
            (build_id, slot),
        )

    cur.close()
    conn.close()
    return build_id

def get_build(build_id: int, user_id: int):
    rows = fetchall(
        """
        SELECT
          b.build_id,
          b.name,
          bp.slot,
          bp.product_id,

          po.title_raw,
          po.image_url,

          -- CPU
          cs.socket            AS cpu_socket,
          cs.cores             AS cpu_cores,
          cs.cpu_model         AS cpu_cpu_model,

          -- MB
          ms.socket            AS mb_socket,
          ms.mb_model            AS mb_mb_model,
          ms.memory_type       AS mb_memory_type,
          ms.memory_slots       AS mb_memory_slots,
          ms.form_factor       AS mb_form_factor,
          ms.max_memory_gb      AS mb_max_memory_gb,

          -- RAM
          rs.memory_type        AS ram_memory_type,
          rs.sticks             AS ram_sticks,
          rs.capacity_per_stick_gb       AS ram_capacity_per_stick_gb,
          rs.speed_mhz          AS ram_speed_mhz,

          -- GPU
          gs.gpu_model         AS gpu_gpu_model,
          gs.vram_gb           AS gpu_vram_gb,

          -- Storage
          ss.series            AS storage_series,
          ss.type             AS storage_type,
          ss.capacity_gb     AS storage_capacity_gb 

        FROM builds b
        LEFT JOIN build_parts bp ON bp.build_id = b.build_id

        LEFT JOIN cpu_specs cs      ON cs.product_id = bp.product_id AND bp.slot = 'cpu'
        LEFT JOIN mb_specs ms       ON ms.product_id = bp.product_id AND bp.slot = 'mb'
        LEFT JOIN ram_specs rs      ON rs.product_id = bp.product_id AND bp.slot = 'ram'
        LEFT JOIN gpu_specs gs      ON gs.product_id = bp.product_id AND bp.slot = 'gpu'
        LEFT JOIN storage_specs ss  ON ss.product_id = bp.product_id AND bp.slot = 'storage'

        LEFT JOIN (
          SELECT po.*
          FROM product_offers po
          JOIN (
            SELECT product_id, MIN(price) AS min_price
            FROM product_offers
            WHERE image_url IS NOT NULL
            GROUP BY product_id
          ) x ON x.product_id = po.product_id AND x.min_price = po.price
        ) po ON po.product_id = bp.product_id

        WHERE b.build_id = %s AND b.user_id = %s
        """,
        (build_id, user_id)
    )

    if not rows:
        return None


    build = {
        "build_id": rows[0]["build_id"],
        "name": rows[0]["name"],
        "parts": {}
    }

    for r in rows:
        slot = r["slot"]
        if not slot or not r["product_id"]:
            continue

        if slot == "cpu":
            build["parts"]["cpu"] = {
                "id": r["product_id"],
                "title": r["title_raw"],
                "model": r["cpu_cpu_model"],
                "image": r["image_url"],
                "socket": r["cpu_socket"],
                "cores": r["cpu_cores"],
                
            }

        elif slot == "mb":
            build["parts"]["mb"] = {
                "id": r["product_id"],
                "title": r["title_raw"],
                "model": r["mb_mb_model"],
                "image": r["image_url"],
                "socket": r["mb_socket"],
                "memory_type": r["mb_memory_type"],
                "memory_slots": r["mb_memory_slots"],
                "max_memory_gb": r["mb_max_memory_gb"],
                "form_factor": r["mb_form_factor"],
                
            }

        elif slot == "ram":
            build["parts"]["ram"] = {
                "id": r["product_id"],
                "title": r["title_raw"],
                "image": r["image_url"],
                "memory_type": r["ram_memory_type"],
                "sticks": r["ram_sticks"],
                "capacity_per_stick_gb": r["ram_capacity_per_stick_gb"],
                "speed_mhz": r["ram_speed_mhz"],
                
            }

        elif slot == "gpu":
            build["parts"]["gpu"] = {
                "id": r["product_id"],
                "title": r["title_raw"],
                "model": r["gpu_gpu_model"],
                "image": r["image_url"],
                "vram": r["gpu_vram_gb"],
                
            }

        elif slot == "storage":
            build["parts"]["storage"] = {
                "id": r["product_id"],
                "title": r["title_raw"],
                "series": r["storage_series"],
                "image": r["image_url"],
                "type": r["storage_type"],
                "capacity_gb": r["storage_capacity_gb"],
                
            
            }

    return build


def get_build_parts(user_id: int, build_id: int):
    rows = fetchall("""
      SELECT b.build_id, b.name, bp.slot, bp.product_id
      FROM builds b
      JOIN build_parts bp ON bp.build_id = b.build_id
      WHERE b.user_id=%s AND b.build_id=%s
    """, (user_id, build_id))
    return rows

def list_builds(user_id: int):
    return fetchall("""
      SELECT build_id, name, updated_at
      FROM builds
      WHERE user_id=%s
      ORDER BY updated_at DESC
    """, (user_id,))

def set_slot(user_id: int, build_id: int, slot: str, product_id: int | None):
    # ensure ownership
    owns = fetchall("SELECT 1 FROM builds WHERE build_id=%s AND user_id=%s LIMIT 1", (build_id, user_id))
    if not owns:
        return False
    execute("UPDATE build_parts SET product_id=%s WHERE build_id=%s AND slot=%s", (product_id, build_id, slot))
    return True

def delete_build(user_id: int, build_id: int):
    execute("DELETE FROM builds WHERE build_id=%s AND user_id=%s", (build_id, user_id))

