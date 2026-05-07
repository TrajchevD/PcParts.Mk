from app.db import fetchall

def get_cpu_by_model(model_key: str):
    rows = fetchall("""
        SELECT socket, cores, threads
        FROM cpu_specs
        WHERE cpu_model = %s
    """, (model_key,))
    return rows[0] if rows else None


def get_mb_by_product(product_id: int):
    rows = fetchall("""
        SELECT socket, memory_type
        FROM mb_specs_v2
        WHERE product_id = %s
    """, (product_id,))
    return rows[0] if rows else None


def get_ram_by_product(product_id: int):
    rows = fetchall("""
        SELECT memory_type
        FROM ram_specs_v2
        WHERE product_id = %s
    """, (product_id,))
    return rows[0] if rows else None

def compute_constraints_v2(selected: dict) -> dict:
    """
    selected = {
      cpu_model,
      mb_product_id,
      ram_product_id,
      gpu_model,
      storage_product_id
    }
    """
    c = {}

    cpu = get_cpu_by_model(selected.get("cpu_model")) if selected.get("cpu_model") else None
    mb  = get_mb_by_product(selected.get("mb_product_id")) if selected.get("mb_product_id") else None

    if cpu:
        c["required_mb_socket"] = cpu["socket"]

    if mb:
        c["required_cpu_socket"] = mb["socket"]
        c["required_ram_type"] = mb["memory_type"]

    if cpu and mb and cpu["socket"] != mb["socket"]:
        c["conflict"] = "CPU socket != Motherboard socket"

    # GPU recommendation (same logic as V1)
    if cpu:
        if cpu["cores"] >= 12:
            c["min_gpu_vram"] = 12
        elif cpu["cores"] >= 8:
            c["min_gpu_vram"] = 8
        else:
            c["min_gpu_vram"] = 6

    return c

def validate_selection_v2(slot: str, value, selected: dict):
    c = compute_constraints_v2(selected)

    if slot == "cpu" and c.get("required_cpu_socket"):
        cpu = get_cpu_by_model(value)
        if not cpu or cpu["socket"] != c["required_cpu_socket"]:
            return False, f"CPU socket must be {c['required_cpu_socket']}"

    if slot == "mb" and c.get("required_mb_socket"):
        mb = get_mb_by_product(value)
        if not mb or mb["socket"] != c["required_mb_socket"]:
            return False, f"Motherboard socket must be {c['required_mb_socket']}"

    if slot == "ram" and c.get("required_ram_type"):
        ram = get_ram_by_product(value)
        if not ram or ram["memory_type"] != c["required_ram_type"]:
            return False, f"RAM type must be {c['required_ram_type']}"

    return True, None
