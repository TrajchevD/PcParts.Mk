# app/services/compare/compare_service.py

from app.db import fetchall


CPU_MODEL_REGEX = (
    "(AMD Ryzen [3579] [0-9]{4}(X3D|X|G|F|AF)?|"
    "Intel Core i[3579]-[0-9]{5}(KF|K|F)?|"
    "Intel Core Ultra [57] [0-9]{3}(KF|K|F)?)"
)

GPU_MODEL_REGEX = (
    "(RTX\\s?(?:20|30|40|50)[0-9]{2,3}\\s?(?:Ti|SUPER)?|"
    "RX\\s?[5679][0-9]{3,4}\\s?(?:XT|XTX)?)"
)


CATEGORY_CONFIG = {
    "cpu": {
        "identity": "model",
        "spec_fields": {
            "socket": "socket",
            "cores": "cores",
            "threads": "threads",
            "base_clock": "base_clock_ghz",
            "boost_clock": "boost_clock_ghz",
            "tdp": "tdp_w",
            "memory_type": "memory_type",
            "brand": "brand",
        },
    },
    "gpu": {
        "identity": "model",
        "spec_fields": {
            "vram": "vram_gb",
            "memory_type": "memory_type",
            "pcie": "pcie_version",
            "length": "length_mm",
            "recommended_psu": "recommended_psu_w",
        },
    },
    "ram": {
        "identity": "product",
        "spec_table": "ram_specs_v2",
        "identity_field": "product_id",
        "model_field": "model",
        "spec_fields": {
            "memory_type": "memory_type",
            "speed": "speed_mhz",
            "cas_latency": "cas_latency",
            "modules": "kit_modules",
            "capacity_per_stick": "capacity_per_stick_gb",
            "total_capacity": "total_capacity_gb",
            "form_factor": "form_factor",
        },
    },
    "mb": {
        "identity": "product",
        "spec_table": "mb_specs_v2",
        "identity_field": "product_id",
        "model_field": "model",
        "spec_fields": {
            "socket": "socket",
            "memory_type": "memory_type",
            "max_ram": "max_ram_mhz",
            "form_factor": "form_factor",
        },
    },
    "storage": {
        "identity": "product",
        "spec_table": "storage_specs_v2",
        "identity_field": "product_id",
        "model_field": "model",
        "spec_fields": {
            "type": "storage_type",
            "interface": "interface",
            "capacity": "capacity_gb",
            "form_factor": "form_factor",
            "protocol": "protocol",
        },
    },
}


def compare_products(category: str, ids: list):

    if category not in CATEGORY_CONFIG:
        raise ValueError("Invalid category")

    if not ids or len(ids) < 1:
        return []

    cfg = CATEGORY_CONFIG[category]
    placeholders = ",".join(["%s"] * len(ids))

    # ================================
    # CPU
    # ================================
    if category == "cpu":

        rows = fetchall(
            f"""
            SELECT
              cs.cpu_model AS identity,
              cs.cpu_model AS model,
              img.image_url,
              cs.socket,
              cs.cores,
              cs.threads,
              cs.base_clock_ghz AS base_clock,
              cs.boost_clock_ghz AS boost_clock,
              cs.tdp_w AS tdp,
              cs.memory_type,
              cs.brand
            FROM cpu_specs cs

            LEFT JOIN (
              SELECT
                REGEXP_SUBSTR(po.title_raw, '{CPU_MODEL_REGEX}') AS model_key,
                MAX(po.image_url) AS image_url
              FROM product_offers po
              WHERE po.currency = 'MKD'
                AND po.price IS NOT NULL
              GROUP BY model_key
            ) img
              ON UPPER(img.model_key) = UPPER(cs.cpu_model)

            WHERE cs.cpu_model IN ({placeholders})
            ORDER BY FIELD(cs.cpu_model, {placeholders})
            """,
            tuple(ids) * 2,
        )

        return [
            {
                "id": r["identity"],
                "model": r["model"],
                "image": r["image_url"],
                "specs": {
                    "socket": r["socket"],
                    "cores": r["cores"],
                    "threads": r["threads"],
                    "base_clock": r["base_clock"],
                    "boost_clock": r["boost_clock"],
                    "tdp": r["tdp"],
                    "memory_type": r["memory_type"],
                    "brand": r["brand"],
                },
            }
            for r in rows
        ]

    # ================================
    # GPU
    # ================================
    if category == "gpu":

        rows = fetchall(
            f"""
            SELECT
              gs.gpu_model AS identity,
              gs.gpu_model AS model,
              img.image_url,
              gs.vram_gb,
              gs.memory_type,
              gs.pcie_version,
              gs.length_mm,
              gs.recommended_psu_w
            FROM gpu_specs gs

            LEFT JOIN (
              SELECT
                REGEXP_SUBSTR(po.title_raw, '{GPU_MODEL_REGEX}') AS model_key,
                MAX(po.image_url) AS image_url
              FROM product_offers po
              WHERE po.currency = 'MKD'
                AND po.price IS NOT NULL
              GROUP BY model_key
            ) img
              ON UPPER(img.model_key) LIKE CONCAT('%', UPPER(gs.gpu_model), '%')

            WHERE gs.gpu_model IN ({placeholders})
            ORDER BY FIELD(gs.gpu_model, {placeholders})
            """,
            tuple(ids) * 2,
        )

        return [
            {
                "id": r["identity"],
                "model": r["model"],
                "image": r["image_url"],
                "specs": {
                    "vram": r["vram_gb"],
                    "memory_type": r["memory_type"],
                    "pcie": r["pcie_version"],
                    "length": r["length_mm"],
                    "recommended_psu": r["recommended_psu_w"],
                },
            }
            for r in rows
        ]

    # ================================
    # RAM / MB / STORAGE
    # ================================

    spec_cols = ", ".join(
        [f"s.{col} AS {key}" for key, col in cfg["spec_fields"].items()]
    )

    rows = fetchall(
        f"""
        SELECT
          s.{cfg['identity_field']} AS identity,
          s.{cfg['model_field']} AS model,
          po.image_url,
          {spec_cols}
        FROM {cfg['spec_table']} s
        LEFT JOIN product_offers po
          ON po.product_id = s.product_id
        WHERE s.{cfg['identity_field']} IN ({placeholders})
        ORDER BY FIELD(s.{cfg['identity_field']}, {placeholders})
        """,
        tuple(ids) * 2,
    )

    return [
        {
            "id": r["identity"],
            "model": r["model"],
            "image": r["image_url"],
            "specs": {k: r[k] for k in cfg["spec_fields"].keys()},
        }
        for r in rows
    ]