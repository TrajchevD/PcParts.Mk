"""
Builder repository — CRUD for builds and build_parts.
All operations that need atomicity (create_build, set_slot, reset_build)
use explicit transactions via get_db() instead of stored procedures,
for compatibility with TiDB Serverless.
"""

from app.core.db import get_db, execute, fetchall, fetchone

SLOTS = ("cpu", "gpu", "mb", "ram", "storage")


# ─── Build CRUD ──────────────────────────────────────────────────

def create_build(user_id: int, name: str) -> int:
    with get_db() as conn:
        conn.autocommit = False
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO builds (user_id, name) VALUES (%s, %s)",
                (user_id, name),
            )
            build_id = cur.lastrowid
            cur.executemany(
                "INSERT INTO build_parts (build_id, slot, product_id) VALUES (%s, %s, NULL)",
                [(build_id, slot) for slot in SLOTS],
            )
            conn.commit()
            cur.close()
            return build_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.autocommit = True


def list_builds(user_id: int) -> list[dict]:
    return fetchall(
        """
        SELECT build_id, name, created_at, updated_at
        FROM builds
        WHERE user_id = %s
        ORDER BY updated_at DESC
        """,
        (user_id,),
    )


def delete_build(build_id: int, user_id: int) -> None:
    execute(
        "DELETE FROM builds WHERE build_id = %s AND user_id = %s",
        (build_id, user_id),
    )


def rename_build(build_id: int, user_id: int, name: str) -> bool:
    execute(
        "UPDATE builds SET name = %s WHERE build_id = %s AND user_id = %s",
        (name, build_id, user_id),
    )
    return True


# ─── Slot management ─────────────────────────────────────────────

def set_slot(build_id: int, user_id: int, slot: str, product_id: int | None) -> None:
    with get_db() as conn:
        conn.autocommit = False
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT build_id FROM builds WHERE build_id = %s AND user_id = %s",
                (build_id, user_id),
            )
            if not cur.fetchone():
                raise PermissionError("Build not found or access denied")
            cur.execute(
                "UPDATE build_parts SET product_id = %s WHERE build_id = %s AND slot = %s",
                (product_id, build_id, slot),
            )
            conn.commit()
            cur.close()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.autocommit = True


def reset_build(build_id: int, user_id: int) -> None:
    with get_db() as conn:
        conn.autocommit = False
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT build_id FROM builds WHERE build_id = %s AND user_id = %s",
                (build_id, user_id),
            )
            if not cur.fetchone():
                raise PermissionError("Build not found or access denied")
            cur.execute(
                "UPDATE build_parts SET product_id = NULL WHERE build_id = %s",
                (build_id,),
            )
            conn.commit()
            cur.close()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.autocommit = True


# ─── Full build load (parts + specs) ─────────────────────────────

def get_build(build_id: int, user_id: int) -> dict | None:
    header = fetchone(
        "SELECT build_id, name FROM builds WHERE build_id = %s AND user_id = %s",
        (build_id, user_id),
    )
    if not header:
        return None

    rows = fetchall(
        """
        SELECT
          bp.slot,
          bp.product_id,
          p.canonical_title,

          co.price       AS best_price,
          co.image_url,
          co.store_id,
          st.name        AS store_name,

          -- CPU
          cs.cpu_model,
          cs.socket      AS cpu_socket,
          cs.cores,
          cs.threads,
          cs.memory_type AS cpu_memory_type,
          cs.tdp_w,

          -- GPU
          gs.gpu_model,
          gs.vram_gb,
          gs.pcie_version       AS gpu_pcie,
          gs.recommended_psu_w,

          -- MB
          mb.mb_model,
          mb.socket      AS mb_socket,
          mb.memory_type AS mb_memory_type,
          mb.memory_slots,
          mb.max_memory_gb,
          mb.form_factor AS mb_form_factor,
          mb.chipset,

          -- RAM
          r.brand        AS ram_brand,
          r.series       AS ram_series,
          r.memory_type  AS ram_memory_type,
          r.total_capacity_gb,
          r.sticks,
          r.speed_mhz,
          r.cas_latency,

          -- Storage
          s.brand        AS storage_brand,
          s.series       AS storage_series,
          s.type         AS storage_type,
          s.capacity_gb,
          s.interface,
          s.form_factor  AS storage_form_factor

        FROM build_parts bp
        LEFT JOIN products p ON p.product_id = bp.product_id
        LEFT JOIN v_cheapest_offers co ON co.product_id = bp.product_id
        LEFT JOIN stores st ON st.store_id = co.store_id

        LEFT JOIN cpu_specs cs     ON cs.product_id = bp.product_id AND bp.slot = 'cpu'
        LEFT JOIN gpu_specs gs     ON gs.product_id = bp.product_id AND bp.slot = 'gpu'
        LEFT JOIN mb_specs mb      ON mb.product_id = bp.product_id AND bp.slot = 'mb'
        LEFT JOIN ram_specs r      ON r.product_id  = bp.product_id AND bp.slot = 'ram'
        LEFT JOIN storage_specs s  ON s.product_id  = bp.product_id AND bp.slot = 'storage'

        WHERE bp.build_id = %s
        """,
        (build_id,),
    )

    build = {
        "build_id": header["build_id"],
        "name": header["name"],
        "parts": {},
    }

    for row in rows:
        slot = row["slot"]
        if not slot or row["product_id"] is None:
            continue

        base = {
            "product_id": row["product_id"],
            "title": row["canonical_title"],
            "best_price": row["best_price"],
            "image_url": row["image_url"],
            "store": row["store_name"],
        }

        if slot == "cpu":
            build["parts"]["cpu"] = {
                **base,
                "specs": {
                    "cpu_model": row["cpu_model"],
                    "socket": row["cpu_socket"],
                    "cores": row["cores"],
                    "threads": row["threads"],
                    "memory_type": row["cpu_memory_type"],
                    "tdp_w": row["tdp_w"],
                },
            }
        elif slot == "gpu":
            build["parts"]["gpu"] = {
                **base,
                "specs": {
                    "gpu_model": row["gpu_model"],
                    "vram_gb": row["vram_gb"],
                    "pcie_version": row["gpu_pcie"],
                    "recommended_psu_w": row["recommended_psu_w"],
                },
            }
        elif slot == "mb":
            build["parts"]["mb"] = {
                **base,
                "specs": {
                    "mb_model": row["mb_model"],
                    "socket": row["mb_socket"],
                    "memory_type": row["mb_memory_type"],
                    "memory_slots": row["memory_slots"],
                    "max_memory_gb": row["max_memory_gb"],
                    "form_factor": row["mb_form_factor"],
                    "chipset": row["chipset"],
                },
            }
        elif slot == "ram":
            build["parts"]["ram"] = {
                **base,
                "specs": {
                    "brand": row["ram_brand"],
                    "series": row["ram_series"],
                    "memory_type": row["ram_memory_type"],
                    "total_capacity_gb": row["total_capacity_gb"],
                    "sticks": row["sticks"],
                    "speed_mhz": row["speed_mhz"],
                    "cas_latency": row["cas_latency"],
                },
            }
        elif slot == "storage":
            build["parts"]["storage"] = {
                **base,
                "specs": {
                    "brand": row["storage_brand"],
                    "series": row["storage_series"],
                    "type": row["storage_type"],
                    "capacity_gb": row["capacity_gb"],
                    "interface": row["interface"],
                    "form_factor": row["storage_form_factor"],
                },
            }

    return build
