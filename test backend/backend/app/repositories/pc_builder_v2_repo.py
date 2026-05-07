from app.db import fetchall, execute


# =========================
# CPU / GPU (model_key)
# =========================
def get_lowest_offer_for_model(model_key: str):
    rows = fetchall("""
        SELECT offer_id, price, store_id
        FROM product_offers
        WHERE price IS NOT NULL
          AND REGEXP_SUBSTR(title_raw, %s) = %s
        ORDER BY price ASC
        LIMIT 1
    """, (model_key, model_key))
    return rows[0] if rows else None


def set_slot_by_model(build_id, slot, model_key):
    print("➡️ set_slot_by_model", build_id, slot, model_key)

    offer = get_lowest_offer_for_model(model_key)
    print("➡️ lowest offer:", offer)

    if not offer:
        return False, "No offers found"

    execute("""
        INSERT INTO build_parts_v2
        (build_id, slot, model_key, selected_offer_id)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
          model_key = VALUES(model_key),
          product_id = NULL,
          selected_offer_id = VALUES(selected_offer_id)
    """, (build_id, slot, model_key, offer["offer_id"]))

    print("✅ INSERT DONE")
    return True, None


# =========================
# MB / RAM / STORAGE (product_id)
# =========================
def get_lowest_offer_for_product(product_id: int):
    rows = fetchall("""
        SELECT offer_id, price, store_id
        FROM product_offers
        WHERE product_id = %s
          AND price IS NOT NULL
        ORDER BY price ASC
        LIMIT 1
    """, (product_id,))
    return rows[0] if rows else None


def set_slot_by_product_id(build_id, slot, product_id):
    print("➡️ set_slot_by_product_id", build_id, slot, product_id)

    offer = get_lowest_offer_for_product(product_id)
    print("➡️ lowest offer:", offer)

    if not offer:
        return False, "No offers found"

    execute("""
        INSERT INTO build_parts_v2
        (build_id, slot, product_id, selected_offer_id)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
          product_id = VALUES(product_id),
          model_key = NULL,
          selected_offer_id = VALUES(selected_offer_id)
    """, (build_id, slot, product_id, offer["offer_id"]))

    print("✅ INSERT DONE")
    return True, None


# =========================
# BUILD LOAD
# =========================
def get_build_v2(build_id: int, user_id: int):
    build_rows = fetchall("""
        SELECT build_id, name
        FROM builds
        WHERE build_id=%s AND user_id=%s
    """, (build_id, user_id))

    if not build_rows:
        return None

    build = {
        "build_id": build_rows[0]["build_id"],
        "name": build_rows[0]["name"],
        "parts": {},
    }

    part_rows = fetchall("""
        SELECT
          bp.slot,
          bp.model_key,
          bp.product_id,
          po.price,
          po.image_url,
          s.name AS store,

          -- CPU
          cs.socket,
          cs.cores,
          cs.threads,

          -- GPU
          gs.vram_gb,
          gs.memory_type AS gpu_memory,
          gs.pcie_version,

          -- MB
          m.model AS mb_model,
          m.socket AS mb_socket,
          m.memory_type AS mb_memory,
          m.form_factor,
          
          -- RAM
          rs.model AS ram_model,              
          rs.memory_type AS ram_memory,
          rs.total_capacity_gb AS ram_capacity,
          rs.speed_mhz AS ram_speed,
          rs.kit_modules AS ram_modules,
          
                         
          ss.model AS storage_model,
          ss.storage_type AS storage_type,
          ss.capacity_gb AS storage_capacity,
          ss.interface AS storage_interface,
          ss.form_factor AS storage_form_factor,
          ss.protocol AS storage_protocol
          
        FROM build_parts_v2 bp
        JOIN product_offers po ON po.offer_id = bp.selected_offer_id
        JOIN stores s ON s.store_id = po.store_id
        LEFT JOIN ram_specs_v2 rs ON rs.product_id = bp.product_id
                        
        LEFT JOIN storage_specs_v2 ss ON ss.product_id = bp.product_id
        LEFT JOIN cpu_specs cs ON cs.cpu_model = bp.model_key
        LEFT JOIN gpu_specs gs
          ON UPPER(
               REPLACE(
                 REPLACE(gs.gpu_model, 'GeForce ', ''),
                 'Radeon ',
                 ''
               )
             ) = UPPER(bp.model_key)

        LEFT JOIN mb_specs_v2 m ON m.product_id = bp.product_id

        WHERE bp.build_id=%s
    """, (build_id,))

    for r in part_rows:
        if r["slot"] == "cpu":
            build["parts"]["cpu"] = {
                "model": r["model_key"],
                "price": r["price"],
                "store": r["store"],
                "image": r["image_url"],
                "specs": {
                    "socket": r["socket"],
                    "cores": r["cores"],
                    "threads": r["threads"],
                },
            }

        elif r["slot"] == "gpu":
            build["parts"]["gpu"] = {
                "model": r["model_key"],
                "price": r["price"],
                "store": r["store"],
                "image": r["image_url"],
                "specs": {
                    "vram": r["vram_gb"],
                    "memory_type": r["gpu_memory"],
                    "pcie": r["pcie_version"],
                },
            }

        elif r["slot"] == "mb":
            build["parts"]["mb"] = {
                "product_id": r["product_id"],
                "model": r["mb_model"],
                "price": r["price"],
                "store": r["store"],
                "image": r["image_url"],
                "specs": {
                    "socket": r["mb_socket"],
                    "memory": r["mb_memory"],
                    "form_factor": r["form_factor"],
                },
            }

        elif r["slot"] == "ram":
            build["parts"]["ram"] = {
                "product_id": r["product_id"],
                "model": r["ram_model"],   # ✅ ADD THIS
                "price": r["price"],
                "store": r["store"],
                "image": r["image_url"],
                "specs": {
                    "memory_type": r["ram_memory"],
                    "capacity": r["ram_capacity"],
                    "speed": r["ram_speed"],
                    "modules": r["ram_modules"],
                },
            }

        elif r["slot"] == "storage":
            build["parts"]["storage"] = {
                "product_id": r["product_id"],
                "model": r["storage_model"],   # ✅ SAME IDEA AS RAM
                "price": r["price"],
                "store": r["store"],
                "image": r["image_url"],
                "specs": {
                    "type": r["storage_type"],
                    "capacity": r["storage_capacity"],
                    "interface": r["storage_interface"],
                    "form_factor": r["storage_form_factor"],
                    "protocol": r["storage_protocol"],
                },
            }




    return build


def remove_slot_v2(build_id: int, slot: str):
    execute(
        "DELETE FROM build_parts_v2 WHERE build_id=%s AND slot=%s",
        (build_id, slot)
    )
