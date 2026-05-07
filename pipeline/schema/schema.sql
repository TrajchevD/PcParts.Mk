-- ============================================================
-- PcPartsMK — Full Database Schema
-- Run once on a fresh database:
--   mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS pc_parts CHARACTER SET utf8mb4;"
--   mysql -u root -p pc_parts < schema/schema.sql
-- ============================================================

USE pc_parts;

SET FOREIGN_KEY_CHECKS = 0;

-- ─── Stores ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS stores (
    store_id   INT          AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(50)  NOT NULL UNIQUE,
    base_url   VARCHAR(255)
);

-- ─── Categories ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS categories (
    category_id INT         AUTO_INCREMENT PRIMARY KEY,
    slug        VARCHAR(30) NOT NULL UNIQUE,
    name        VARCHAR(50) NOT NULL
);

INSERT IGNORE INTO categories (slug, name) VALUES
    ('cpu',     'Processors'),
    ('gpu',     'Graphics Cards'),
    ('ram',     'Memory'),
    ('mb',      'Motherboards'),
    ('storage', 'Storage'),
    ('memory',  'Storage');   -- alias used by Neptun/Setec scrapers

-- ─── Products (canonical, deduplicated across stores) ────────
CREATE TABLE IF NOT EXISTS products (
    product_id      INT          AUTO_INCREMENT PRIMARY KEY,
    category_id     INT          NOT NULL,
    canonical_title VARCHAR(500) NOT NULL,
    model_key       VARCHAR(150) NULL,
    spec_status     ENUM('pending','ok','failed') NOT NULL DEFAULT 'pending',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    UNIQUE KEY uq_model_key_cat (model_key, category_id),
    INDEX idx_spec_status (spec_status),
    INDEX idx_category    (category_id)
);

-- ─── Product offers (one row per product × store) ────────────
CREATE TABLE IF NOT EXISTS product_offers (
    offer_id     INT           AUTO_INCREMENT PRIMARY KEY,
    product_id   INT           NOT NULL,
    store_id     INT           NOT NULL,
    title_raw    VARCHAR(500),
    price        DECIMAL(10,2),
    price_text   VARCHAR(50),
    product_url  VARCHAR(1000),
    image_url    VARCHAR(1000),
    in_stock     TINYINT(1)    NOT NULL DEFAULT 1,
    last_seen_at DATETIME      DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (store_id)   REFERENCES stores(store_id),
    UNIQUE KEY uq_product_store (product_id, store_id),
    INDEX idx_in_stock   (in_stock),
    INDEX idx_last_seen  (last_seen_at),
    INDEX idx_price      (price)
);

-- ─── Price history ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS offer_price_history (
    history_id INT          AUTO_INCREMENT PRIMARY KEY,
    offer_id   INT          NOT NULL,
    price      DECIMAL(10,2),
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (offer_id) REFERENCES product_offers(offer_id),
    INDEX idx_changed_at (changed_at)
);

-- ─── Spec tables ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS cpu_specs (
    product_id       INT            PRIMARY KEY,
    cpu_model        VARCHAR(100),
    brand            VARCHAR(30),
    socket           VARCHAR(20),
    cores            INT,
    threads          INT,
    base_clock_ghz   DECIMAL(4,2),
    boost_clock_ghz  DECIMAL(4,2),
    tdp_w            INT,
    memory_type      VARCHAR(10),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS gpu_specs (
    product_id          INT          PRIMARY KEY,
    gpu_model           VARCHAR(100),
    vram_gb             INT,
    memory_type         VARCHAR(10),
    pcie_version        VARCHAR(5),
    length_mm           INT,
    recommended_psu_w   INT,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS mb_specs (
    product_id    INT          PRIMARY KEY,
    mb_model      VARCHAR(150),
    brand         VARCHAR(30),
    chipset       VARCHAR(20),
    socket        VARCHAR(20),
    form_factor   VARCHAR(20),
    memory_type   VARCHAR(10),
    memory_slots  INT,
    max_memory_gb INT,
    pcie_version  VARCHAR(5),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS ram_specs (
    product_id           INT         PRIMARY KEY,
    brand                VARCHAR(50),
    series               VARCHAR(100),
    memory_type          VARCHAR(10),
    total_capacity_gb    INT,
    sticks               INT,
    capacity_per_stick_gb INT,
    speed_mhz            INT,
    cas_latency          INT,
    expo                 TINYINT(1)  DEFAULT 0,
    xmp                  TINYINT(1)  DEFAULT 0,
    ecc                  TINYINT(1)  DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS storage_specs (
    product_id   INT         PRIMARY KEY,
    type         VARCHAR(10),
    brand        VARCHAR(50),
    series       VARCHAR(100),
    capacity_gb  INT,
    form_factor  VARCHAR(10),
    interface    VARCHAR(10),
    pcie_version VARCHAR(5),
    rpm          INT,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- ─── Price alerts & notifications ────────────────────────────

CREATE TABLE IF NOT EXISTS price_alerts (
    alert_id     INT           AUTO_INCREMENT PRIMARY KEY,
    user_id      INT           NOT NULL,
    alert_name   VARCHAR(100),
    category_slug VARCHAR(30),
    title_query  VARCHAR(200),
    store_name   VARCHAR(50),
    max_price    DECIMAL(10,2),
    status       ENUM('ACTIVE','TRIGGERED','PAUSED') DEFAULT 'ACTIVE',
    triggered_at DATETIME,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alert_state (
    id              INT PRIMARY KEY,
    last_checked_at DATETIME
);
INSERT IGNORE INTO alert_state (id, last_checked_at) VALUES (1, NULL);

CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT  AUTO_INCREMENT PRIMARY KEY,
    user_id         INT  NOT NULL,
    alert_id        INT,
    title           VARCHAR(200),
    message         TEXT,
    payload         JSON,
    is_read         TINYINT(1) DEFAULT 0,
    created_at      DATETIME   DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alert_id) REFERENCES price_alerts(alert_id)
);

-- ─── Useful view: cheapest in-stock offer per product ────────
CREATE OR REPLACE VIEW v_cheapest_offers AS
SELECT po.*
FROM product_offers po
INNER JOIN (
    SELECT product_id, MIN(price) AS min_price
    FROM product_offers
    WHERE in_stock = 1 AND price IS NOT NULL
    GROUP BY product_id
) m ON m.product_id = po.product_id
   AND m.min_price  = po.price
WHERE po.in_stock = 1;

SET FOREIGN_KEY_CHECKS = 1;

SELECT 'Schema ready' AS status;
