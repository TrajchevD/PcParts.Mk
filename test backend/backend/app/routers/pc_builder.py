from fastapi import APIRouter, Depends, HTTPException
from app.auth.dependencies import get_current_user
from app.db import fetchall
from app.schemas.pc_builder import BuildCreateIn, SlotUpdateIn, OptionsIn
from app.repositories.pc_builder_repo import (
    create_build,
    list_builds,
    get_build_parts,
    set_slot,
    delete_build,
    get_build
)
from app.repositories.parts_repo import (
    search_cpus,
    search_mbs,
    search_ram,
    search_gpus,
    search_storage,
)
from app.services.compat_service import compute_constraints, validate_selection
from app.repositories.parts_repo import search_cpus


router = APIRouter(prefix="/api/pc-builder", tags=["pc-builder"])

@router.post("/builds")
def create_build_api(body: BuildCreateIn, user=Depends(get_current_user)):
    build_id = create_build(user["user_id"], body.name)
    return {"build_id": build_id}

@router.get("/builds")
def list_builds_api(user=Depends(get_current_user)):
    return list_builds(user["user_id"])

# @router.get("/builds/{build_id}")
# def get_build_api(build_id: int, user=Depends(get_current_user)):
#     rows = get_build_parts(user["user_id"], build_id)
#     if not rows:
#         raise HTTPException(404, "Build not found")

#     parts = {r["slot"]: r["product_id"] for r in rows}
#     selected = {
#         "cpu_id": parts.get("cpu"),
#         "mb_id": parts.get("mb"),
#         "ram_id": parts.get("ram"),
#         "gpu_id": parts.get("gpu"),
#         "storage_id": parts.get("storage"),
#     }
#     constraints = compute_constraints(selected)
#     return {"build_id": build_id, "name": rows[0]["name"], "parts": parts, "constraints": constraints}
@router.get("/builds/{build_id}")
def get_build_api(build_id: int, user=Depends(get_current_user)):
    build = get_build(build_id, user["user_id"])
    if not build:
        raise HTTPException(404, "Build not found")

    constraints = compute_constraints(build["parts"])
    build["constraints"] = constraints

    return build


@router.put("/builds/{build_id}/slots/{slot}")
def set_slot_api(build_id: int, slot: str, body: SlotUpdateIn, user=Depends(get_current_user)):
    # load current build state first
    rows = get_build_parts(user["user_id"], build_id)
    if not rows:
        raise HTTPException(404, "Build not found")

    parts = {r["slot"]: r["product_id"] for r in rows}
    selected = {
        "cpu_id": parts.get("cpu"),
        "mb_id": parts.get("mb"),
        "ram_id": parts.get("ram"),
        "gpu_id": parts.get("gpu"),
        "storage_id": parts.get("storage"),
    }

    # validate new selection (if setting non-null)
    if body.product_id is not None:
        ok, reason = validate_selection(slot, body.product_id, selected)
        if not ok:
            raise HTTPException(400, reason)

    ok2 = set_slot(user["user_id"], build_id, slot, body.product_id)
    if not ok2:
        raise HTTPException(404, "Build not found")

    return {"ok": True}


@router.delete("/builds/{build_id}")
def delete_build_api(build_id: int, user=Depends(get_current_user)):
    delete_build(user["user_id"], build_id)
    return {"ok": True}

@router.get("/mb-sockets")
def get_mb_sockets(user=Depends(get_current_user)):
    rows = fetchall("""
        SELECT DISTINCT socket
        FROM mb_specs
        WHERE socket IS NOT NULL
        ORDER BY socket
    """)
    return [r["socket"] for r in rows]


# @router.post("/options")
# def options_api(body: OptionsIn, user=Depends(get_current_user)):
#     # compute constraints from selected ids passed in
#     constraints = compute_constraints(body.selected)

#     # slot-specific
#     if body.slot == "cpu":
#         socket = constraints.get("required_cpu_socket")
#         rows = search_cpus(body.search, socket, body.limit, body.offset)
#         return {"constraints": constraints, "items": rows}

#     # TODO: implement mb/ram/gpu/storage similarly
#     return {"constraints": constraints, "items": []}

from app.repositories.pc_builder_repo import get_build_parts

@router.post("/options")
def options_api(body: OptionsIn, user=Depends(get_current_user)):
    # 1️⃣ Load build state from DB
    rows = get_build_parts(user["user_id"], body.build_id)
    if not rows:
        raise HTTPException(404, "Build not found")

    # 2️⃣ Build selected dict exactly as compat_service expects
    selected = {
        "cpu_id": None,
        "mb_id": None,
        "ram_id": None,
        "gpu_id": None,
        "storage_id": None,
    }

    for r in rows:
        selected[f"{r['slot']}_id"] = r["product_id"]

    # 3️⃣ Compute constraints from DB-truth
    constraints = compute_constraints(selected)

    slot = body.slot

    # 4️⃣ Slot-specific queries
    if slot == "cpu":
        rows = search_cpus(
            search=body.search,
            socket=constraints.get("required_cpu_socket"),
            filters=body.filters,
            sort=body.sort,                  # ✅ CORRECT
            limit=body.limit,
            offset=body.offset,
        )

        return {"constraints": constraints, "items": rows}

    if slot == "mb":
        rows = search_mbs(
            body.search,
            constraints.get("required_mb_socket"),
            constraints.get("required_ram_type"),
            filters=body.filters,
            sort=body.sort,                   # ✅ CORRECT
            limit=body.limit,
            offset=body.offset,
        )
        return {"constraints": constraints, "items": rows}

    if slot == "ram":
        rows = search_ram(
            body.search,
            constraints.get("required_ram_type"),
            body.filters,
            body.sort,
            body.limit,
            body.offset,
        )
        return {"constraints": constraints, "items": rows}
    
    if slot == "gpu":
        rows = search_gpus(
            body.search,
            body.filters,
            body.sort,
            body.limit,
            body.offset,
        )
        return {"constraints": constraints, "items": rows}
    
    if slot == "storage":
        rows = search_storage(
            body.search,
            body.filters,
            body.sort,
            body.limit,
            body.offset,
        )
        return {"constraints": constraints, "items": rows}

    raise HTTPException(400, "Invalid slot")


# def compute_constraints(parts: dict):
#     cpu = parts.get("cpu")
#     mb = parts.get("mb")
#     ram = parts.get("ram")

#     errors = []

#     if cpu and mb and cpu["socket"] != mb["socket"]:
#         errors.append("CPU and motherboard socket mismatch")

#     if ram and mb and ram["memory_type"] != mb["memory_type"]:
#         errors.append("RAM type incompatible with motherboard")

#     return {
#         "valid": len(errors) == 0,
#         "errors": errors
#     }
