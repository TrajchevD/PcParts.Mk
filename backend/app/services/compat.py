"""
Unified compatibility service.

All slots use product_id. Constraints flow from CPU and MB specs:
  CPU socket  → required MB socket
  MB socket   → required CPU socket
  CPU/MB memory_type → required RAM memory_type
  CPU cores   → suggested minimum GPU VRAM tier
"""

from app.core.constants import (
    VRAM_HIGH_CORES_THRESHOLD,
    VRAM_HIGH_GB,
    VRAM_LOW_GB,
    VRAM_MID_CORES_THRESHOLD,
    VRAM_MID_GB,
)
from app.repositories.parts import (
    get_cpu_specs,
    get_gpu_specs,
    get_mb_specs,
    get_ram_specs,
)


def compute_constraints(selected: dict) -> dict:
    """
    selected keys (all optional, None = not yet chosen):
      cpu_id, gpu_id, mb_id, ram_id, storage_id
    """
    constraints: dict = {}
    errors: list[str] = []

    cpu = get_cpu_specs(selected["cpu_id"]) if selected.get("cpu_id") else None
    mb  = get_mb_specs(selected["mb_id"])  if selected.get("mb_id")  else None

    if cpu:
        constraints["required_mb_socket"]  = cpu["socket"]
        constraints["required_ram_type"]   = cpu.get("memory_type")  # DDR4 / DDR5
        cores = cpu.get("cores") or 0
        if cores >= VRAM_HIGH_CORES_THRESHOLD:
            constraints["suggested_min_vram"] = VRAM_HIGH_GB
        elif cores >= VRAM_MID_CORES_THRESHOLD:
            constraints["suggested_min_vram"] = VRAM_MID_GB
        else:
            constraints["suggested_min_vram"] = VRAM_LOW_GB

    if mb:
        constraints["required_cpu_socket"] = mb["socket"]
        # Only set RAM type from MB if CPU hasn't already set it
        if not constraints.get("required_ram_type"):
            constraints["required_ram_type"] = mb.get("memory_type")

    # Cross-check socket conflict
    if cpu and mb and cpu["socket"] != mb["socket"]:
        errors.append(
            f"Socket conflict: CPU requires {cpu['socket']}, MB has {mb['socket']}"
        )

    # Cross-check memory type conflict (cpu_specs.memory_type vs mb_specs.memory_type)
    if cpu and mb:
        cpu_mem = cpu.get("memory_type")
        mb_mem  = mb.get("memory_type")
        if cpu_mem and mb_mem and cpu_mem != mb_mem:
            errors.append(
                f"Memory type conflict: CPU supports {cpu_mem}, MB uses {mb_mem}"
            )

    if errors:
        constraints["errors"] = errors

    return constraints


def validate_selection(
    slot: str,
    product_id: int,
    selected: dict,
) -> tuple[bool, str | None]:
    """
    Validates a new product_id for `slot` against the current selection.
    Returns (True, None) if valid, (False, reason) if not.
    """
    c = compute_constraints(selected)

    if slot == "cpu":
        required_socket = c.get("required_cpu_socket")
        if required_socket:
            cpu = get_cpu_specs(product_id)
            if not cpu or cpu["socket"] != required_socket:
                return False, f"CPU socket must be {required_socket}"

    elif slot == "mb":
        required_socket = c.get("required_mb_socket")
        if required_socket:
            mb = get_mb_specs(product_id)
            if not mb or mb["socket"] != required_socket:
                return False, f"Motherboard socket must be {required_socket}"
        # Also check memory type matches CPU
        required_ram = c.get("required_ram_type")
        if required_ram:
            mb = get_mb_specs(product_id)
            if mb and mb.get("memory_type") and mb["memory_type"] != required_ram:
                return False, f"Motherboard memory type {mb['memory_type']} conflicts with {required_ram}"

    elif slot == "ram":
        required_type = c.get("required_ram_type")
        if required_type:
            ram = get_ram_specs(product_id)
            if not ram or ram["memory_type"] != required_type:
                return False, f"RAM must be {required_type}"

    return True, None
