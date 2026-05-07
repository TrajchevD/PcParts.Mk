"""
Unified PC Builder — /api/builder

All slots use product_id. Replaces both /api/pc-builder and /api/pc-builder-v2.
Compatibility is enforced on every slot update:
  - CPU socket ↔ MB socket
  - CPU/MB memory_type ↔ RAM memory_type
"""

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user
from app.repositories import builder as repo
from app.repositories.parts import (
    search_cpus,
    search_gpus,
    search_mbs,
    search_ram,
    search_storage,
)
from app.schemas.builder import BuildCreateIn, BuildRenameIn, OptionsIn, SlotUpdateIn
from app.services.compat import compute_constraints, validate_selection

router = APIRouter(prefix="/api/builder", tags=["builder"])

VALID_SLOTS = {"cpu", "gpu", "mb", "ram", "storage"}


# ─── Build CRUD ──────────────────────────────────────────────────

@router.post("/builds", status_code=201)
def create_build(body: BuildCreateIn, user=Depends(get_current_user)):
    build_id = repo.create_build(user["user_id"], body.name)
    return {"build_id": build_id}


@router.get("/builds")
def list_builds(user=Depends(get_current_user)):
    return repo.list_builds(user["user_id"])


@router.get("/builds/{build_id}")
def get_build(build_id: int, user=Depends(get_current_user)):
    build = repo.get_build(build_id, user["user_id"])
    if not build:
        raise HTTPException(404, "Build not found")

    selected = _selected_from_build(build)
    build["constraints"] = compute_constraints(selected)
    return build


@router.patch("/builds/{build_id}")
def rename_build(build_id: int, body: BuildRenameIn, user=Depends(get_current_user)):
    build = repo.get_build(build_id, user["user_id"])
    if not build:
        raise HTTPException(404, "Build not found")
    repo.rename_build(build_id, user["user_id"], body.name)
    return {"ok": True}


@router.delete("/builds/{build_id}", status_code=204)
def delete_build(build_id: int, user=Depends(get_current_user)):
    build = repo.get_build(build_id, user["user_id"])
    if not build:
        raise HTTPException(404, "Build not found")
    repo.delete_build(build_id, user["user_id"])


# ─── Slot management ─────────────────────────────────────────────

@router.put("/builds/{build_id}/slots/{slot}")
def set_slot(
    build_id: int,
    slot: str,
    body: SlotUpdateIn,
    user=Depends(get_current_user),
):
    if slot not in VALID_SLOTS:
        raise HTTPException(400, f"Invalid slot. Must be one of {VALID_SLOTS}")

    build = repo.get_build(build_id, user["user_id"])
    if not build:
        raise HTTPException(404, "Build not found")

    if body.product_id is not None:
        # Validate against the OTHER parts already in the build (not the slot being set)
        selected = _selected_from_build(build)
        selected[f"{slot}_id"] = None  # exclude the slot being updated from constraint checks
        ok, reason = validate_selection(slot, body.product_id, selected)
        if not ok:
            raise HTTPException(400, reason)

    try:
        repo.set_slot(build_id, user["user_id"], slot, body.product_id)
    except PermissionError as exc:
        raise HTTPException(404, str(exc))

    return {"ok": True}


@router.delete("/builds/{build_id}/slots", status_code=204)
def reset_build(build_id: int, user=Depends(get_current_user)):
    """Clear all component slots in a build without deleting the build itself."""
    try:
        repo.reset_build(build_id, user["user_id"])
    except PermissionError as exc:
        raise HTTPException(404, str(exc))


# ─── Options (parts search with compatibility constraints) ────────

@router.post("/options")
def get_options(body: OptionsIn, user=Depends(get_current_user)):
    build = repo.get_build(body.build_id, user["user_id"])
    if not build:
        raise HTTPException(404, "Build not found")

    selected = _selected_from_build(build)
    constraints = compute_constraints(selected)

    slot = body.slot
    common = dict(
        search=body.search,
        filters=body.filters,
        sort=body.sort,
        limit=body.limit,
        offset=body.offset,
    )

    if slot == "cpu":
        items = search_cpus(
            socket=constraints.get("required_cpu_socket"),
            **common,
        )
    elif slot == "gpu":
        items = search_gpus(**common)
    elif slot == "mb":
        items = search_mbs(
            socket=constraints.get("required_mb_socket"),
            memory_type=constraints.get("required_ram_type"),
            **common,
        )
    elif slot == "ram":
        items = search_ram(
            memory_type=constraints.get("required_ram_type"),
            **common,
        )
    elif slot == "storage":
        items = search_storage(**common)
    else:
        raise HTTPException(400, "Invalid slot")

    return {"constraints": constraints, "items": items}


# ─── Utility endpoints ───────────────────────────────────────────

@router.get("/sockets")
def list_sockets():
    """Returns all distinct MB sockets — useful for filter dropdowns."""
    from app.core.db import fetchall
    rows = fetchall(
        "SELECT DISTINCT socket FROM mb_specs WHERE socket IS NOT NULL ORDER BY socket"
    )
    return [r["socket"] for r in rows]


# ─── Helpers ─────────────────────────────────────────────────────

def _selected_from_build(build: dict) -> dict:
    parts = build.get("parts", {})
    return {
        "cpu_id":     (parts.get("cpu") or {}).get("product_id"),
        "gpu_id":     (parts.get("gpu") or {}).get("product_id"),
        "mb_id":      (parts.get("mb") or {}).get("product_id"),
        "ram_id":     (parts.get("ram") or {}).get("product_id"),
        "storage_id": (parts.get("storage") or {}).get("product_id"),
    }
