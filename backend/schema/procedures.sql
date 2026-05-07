-- ============================================================
-- PcPartsMK — Stored Procedures
-- Run after additions.sql:
--   mysql -u root -p pc_parts < schema/procedures.sql
-- ============================================================

-- ─────────────────────────────────────────────────────────────
-- sp_create_build
-- Atomically inserts a build row and all 5 empty slot rows.
-- Stored procedure justification: two dependent INSERTs must
-- succeed together; doing this in the app layer requires manual
-- transaction management and two round-trips.
-- ─────────────────────────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_create_build;

DELIMITER $$
CREATE PROCEDURE sp_create_build(
    IN  p_user_id INT,
    IN  p_name    VARCHAR(100)
)
BEGIN
    DECLARE v_build_id INT;

    INSERT INTO builds (user_id, name) VALUES (p_user_id, p_name);
    SET v_build_id = LAST_INSERT_ID();

    INSERT INTO build_parts (build_id, slot, product_id) VALUES
        (v_build_id, 'cpu',     NULL),
        (v_build_id, 'gpu',     NULL),
        (v_build_id, 'mb',      NULL),
        (v_build_id, 'ram',     NULL),
        (v_build_id, 'storage', NULL);

    SELECT v_build_id AS build_id;
END $$
DELIMITER ;


-- ─────────────────────────────────────────────────────────────
-- sp_set_build_slot
-- Atomically verifies build ownership then updates the slot.
-- Stored procedure justification: ownership check + UPDATE must
-- be atomic to prevent TOCTOU races; one round-trip vs. two.
-- ─────────────────────────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_set_build_slot;

DELIMITER $$
CREATE PROCEDURE sp_set_build_slot(
    IN p_build_id   INT,
    IN p_user_id    INT,
    IN p_slot       VARCHAR(10),
    IN p_product_id INT          -- NULL = clear the slot
)
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM builds
        WHERE build_id = p_build_id AND user_id = p_user_id
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Build not found or access denied';
    END IF;

    UPDATE build_parts
    SET    product_id = p_product_id
    WHERE  build_id = p_build_id
      AND  slot     = p_slot;
END $$
DELIMITER ;

-- ─────────────────────────────────────────────────────────────
-- sp_reset_build
-- Atomically verifies ownership then clears all 5 slot rows.
-- Stored procedure justification: ownership check + bulk UPDATE
-- must be atomic to prevent TOCTOU races; one round-trip vs. two.
-- ─────────────────────────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_reset_build;

DELIMITER $$
CREATE PROCEDURE sp_reset_build(
    IN p_build_id INT,
    IN p_user_id  INT
)
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM builds
        WHERE build_id = p_build_id AND user_id = p_user_id
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Build not found or access denied';
    END IF;

    UPDATE build_parts
    SET    product_id = NULL
    WHERE  build_id = p_build_id;
END $$
DELIMITER ;

SELECT 'Procedures ready' AS status;
