from app.db import fetchall


def _get_cpu(product_id: int):
    rows = fetchall(
        "SELECT socket FROM cpu_specs WHERE product_id=%s",
        (product_id,)
    )
    return rows[0] if rows else None


def _get_mb(product_id: int):
    rows = fetchall(
        "SELECT socket, memory_type FROM mb_specs WHERE product_id=%s",
        (product_id,)
    )
    return rows[0] if rows else None


def _get_ram(product_id: int):
    rows = fetchall(
        "SELECT memory_type FROM ram_specs WHERE product_id=%s",
        (product_id,)
    )
    return rows[0] if rows else None

# app/services/compat_service.py

def get_cpu_specs(product_id: int):
    rows = fetchall("""
        SELECT socket, cores, threads
        FROM cpu_specs
        WHERE product_id=%s
    """, (product_id,))
    return rows[0] if rows else None


def recommend_gpu_constraints(selected: dict) -> dict:
    cpu_id = selected.get("cpu_id")
    if not cpu_id:
        return {}

    cpu = get_cpu_specs(cpu_id)
    if not cpu:
        return {}

    if cpu["cores"] >= 12:
        return {"min_gpu_vram": 12}
    elif cpu["cores"] >= 8:
        return {"min_gpu_vram": 8}
    else:
        return {"min_gpu_vram": 6}


def compute_constraints(selected: dict) -> dict:
    """
    selected keys:
    cpu_id, mb_id, ram_id, gpu_id, storage_id
    """
    c = {}

    cpu_id = selected.get("cpu_id")
    mb_id = selected.get("mb_id")

    cpu = _get_cpu(cpu_id) if cpu_id else None
    mb = _get_mb(mb_id) if mb_id else None

    if cpu:
        c["required_mb_socket"] = cpu["socket"]

    if mb:
        c["required_cpu_socket"] = mb["socket"]
        c["required_ram_type"] = mb["memory_type"]

    if cpu and mb and cpu["socket"] != mb["socket"]:
        c["conflict"] = "CPU socket != Motherboard socket"

    gpu_constraints = recommend_gpu_constraints(selected)
    c.update(gpu_constraints)

    return c


def validate_selection(slot: str, product_id: int, selected: dict) -> tuple[bool, str | None]:
    c = compute_constraints(selected)

    if slot == "cpu" and c.get("required_cpu_socket"):
        cpu = _get_cpu(product_id)
        if not cpu or cpu["socket"] != c["required_cpu_socket"]:
            return False, f"CPU socket must be {c['required_cpu_socket']}"

    if slot == "mb" and c.get("required_mb_socket"):
        mb = _get_mb(product_id)
        if not mb or mb["socket"] != c["required_mb_socket"]:
            return False, f"Motherboard socket must be {c['required_mb_socket']}"

    if slot == "ram" and c.get("required_ram_type"):
        ram = _get_ram(product_id)
        if not ram or ram["memory_type"] != c["required_ram_type"]:
            return False, f"RAM type must be {c['required_ram_type']}"

    return True, None
