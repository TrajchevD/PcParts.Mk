-- ============================================================
-- PcPartsMK — Missing table additions
-- Run once after schema.sql:
--   mysql -u root -p pc_parts < schema/additions.sql
-- ============================================================

USE pc_parts;

SET FOREIGN_KEY_CHECKS = 0;

-- ─── Users ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    user_id       INT          AUTO_INCREMENT PRIMARY KEY,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP
);

-- ─── PC Builds ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS builds (
    build_id   INT          AUTO_INCREMENT PRIMARY KEY,
    user_id    INT          NOT NULL,
    name       VARCHAR(100) NOT NULL DEFAULT 'My Build',
    created_at DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user (user_id)
);

-- ─── Build Parts (one row per slot per build) ────────────────
CREATE TABLE IF NOT EXISTS build_parts (
    build_id   INT                                          NOT NULL,
    slot       ENUM('cpu','gpu','mb','ram','storage')       NOT NULL,
    product_id INT                                          NULL,
    PRIMARY KEY (build_id, slot),
    FOREIGN KEY (build_id)   REFERENCES builds(build_id)   ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE SET NULL
);

SET FOREIGN_KEY_CHECKS = 1;

SELECT 'Additions applied' AS status;
