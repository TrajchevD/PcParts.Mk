from fastapi import APIRouter, Depends, HTTPException
from app.auth.dependencies import get_current_user
from app.db import fetchall, execute

from app.repositories.pc_builder_v2_repo import (
    set_slot_by_model,
    set_slot_by_product_id,
    get_build_v2,
    remove_slot_v2
)

from app.services.compatibility.compat_v2 import (
    validate_selection_v2,
    compute_constraints_v2
)

router = APIRouter(prefix="/api/pc-builder-v2", tags=["pc-builder-v2"])


# ======================================================
# SET / REMOVE SLOT (WITH COMPATIBILITY CHECK)
# ======================================================
@router.put("/builds/{build_id}/slots/{slot}")
def set_slot_v2(build_id: int, slot: str, body: dict, user=Depends(get_current_user)):
    value = body.get("model")

    # Load build (ownership + current state)
    build = get_build_v2(build_id, user["user_id"])
    if not build:
        raise HTTPException(404, "Build not found")

    # REMOVE SLOT
    if value is None:
        remove_slot_v2(build_id, slot)
        return {"ok": True}

    if not value:
        raise HTTPException(400, "model is required")

    # ----------------------------------
    # Build selected map for compatibility
    # ----------------------------------
    selected = {
        "cpu_model": build["parts"].get("cpu", {}).get("model"),
        "gpu_model": build["parts"].get("gpu", {}).get("model"),
        "mb_product_id": build["parts"].get("mb", {}).get("product_id"),
        "ram_product_id": build["parts"].get("ram", {}).get("product_id"),
        "storage_product_id": build["parts"].get("storage", {}).get("product_id"),
    }

    # Override the slot being set
    if slot in ("cpu", "gpu"):
        selected[f"{slot}_model"] = value
    elif slot in ("mb", "ram", "storage"):
        selected[f"{slot}_product_id"] = int(value)
    else:
        raise HTTPException(400, f"Unknown slot: {slot}")

    # ----------------------------------
    # VALIDATE COMPATIBILITY
    # ----------------------------------
    ok, reason = validate_selection_v2(slot, value, selected)
    if not ok:
        raise HTTPException(400, reason)

    # ----------------------------------
    # SAVE SLOT
    # ----------------------------------
    if slot in ("cpu", "gpu"):
        ok, reason = set_slot_by_model(build_id, slot, value)
    else:
        ok, reason = set_slot_by_product_id(build_id, slot, int(value))

    if not ok:
        raise HTTPException(400, reason)

    return {"ok": True}

# ==========================================
# GET ALL BUILDS FOR USER
# ==========================================
@router.get("/builds")
def get_user_builds(user=Depends(get_current_user)):
    rows = fetchall("""
        SELECT build_id, name
        FROM builds
        WHERE user_id=%s
        ORDER BY build_id DESC
    """, (user["user_id"],))

    return {"builds": rows}
# ==========================================
# CREATE BUILD
# ==========================================
@router.post("/builds")
def create_build(body: dict, user=Depends(get_current_user)):
    name = body.get("name", "New Build")

    execute("""
        INSERT INTO builds (user_id, name)
        VALUES (%s, %s)
    """, (user["user_id"], name))

    # Now fetch newest build for this user
    row = fetchall("""
        SELECT build_id
        FROM builds
        WHERE user_id=%s
        ORDER BY build_id DESC
        LIMIT 1
    """, (user["user_id"],))

    build_id = row[0]["build_id"]

    return {"build_id": build_id}



# ======================================================
# LOAD BUILD (WITH CONSTRAINTS)
# ======================================================
@router.get("/builds/{build_id}")
def get_build_v2_api(build_id: int, user=Depends(get_current_user)):
    build = get_build_v2(build_id, user["user_id"])
    if not build:
        raise HTTPException(404, "Build not found")

    selected = {
        "cpu_model": build["parts"].get("cpu", {}).get("model"),
        "gpu_model": build["parts"].get("gpu", {}).get("model"),
        "mb_product_id": build["parts"].get("mb", {}).get("product_id"),
        "ram_product_id": build["parts"].get("ram", {}).get("product_id"),
        "storage_product_id": build["parts"].get("storage", {}).get("product_id"),
    }

    build["constraints"] = compute_constraints_v2(selected)
    return build


# ======================================================
# OPTIONS ENDPOINT (FUTURE – FILTERING WITH RULES)
# ======================================================
@router.post("/options")
def get_options_v2(selected: dict, user=Depends(get_current_user)):
    """
    selected example:
    {
      "cpu_model": "...",
      "mb_product_id": 123,
      ...
    }
    """
    constraints = compute_constraints_v2(selected)

    # TODO:
    # - apply constraints to SQL queries
    # - return filtered options per slot

    return {
        "constraints": constraints,
        "options": []
    }


# ==========================================
# DELETE BUILD
# ==========================================
@router.delete("/builds/{build_id}")
def delete_build(build_id: int, user=Depends(get_current_user)):
    execute("""
        DELETE FROM builds
        WHERE build_id=%s AND user_id=%s
    """, (build_id, user["user_id"]))

    return {"ok": True}


# ==========================================
# RENAME BUILD
# ==========================================
@router.patch("/builds/{build_id}")
def rename_build(build_id: int, body: dict, user=Depends(get_current_user)):
    new_name = body.get("name")

    if not new_name:
        raise HTTPException(400, "name required")

    execute("""
        UPDATE builds
        SET name=%s
        WHERE build_id=%s AND user_id=%s
    """, (new_name, build_id, user["user_id"]))

    return {"ok": True}
